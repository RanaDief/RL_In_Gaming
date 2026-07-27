"""Build the reproducible Maze Hunt greybox level in the current UE project.

Run from Unreal Editor's Python console:
    exec(open(unreal.Paths.project_content_dir() + "Python/build_maze_prototype.py").read())
"""

import unreal


MAP_PATH = "/Game/MazeHunt/MazePrototype"
WALL_HEIGHT = 350.0
WALL_THICKNESS = 50.0
CORRIDOR_WIDTH = 350.0
FLOOR_THICKNESS = 20.0
SHOW_DEBUG_LABELS = True

CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
GREY_MATERIAL = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
WALL_MATERIAL = GREY_MATERIAL
EDITOR_ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def color_material(name, color):
    """Create or reuse a persistent, unlit-looking greybox color material."""
    package_path = "/Game/MazeHunt/Materials"
    asset_path = "{}/{}".format(package_path, name)
    existing = unreal.load_asset(asset_path)
    if existing:
        return existing

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = asset_tools.create_asset(
        name,
        package_path,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    if not material:
        raise RuntimeError("Could not create material {}".format(asset_path))

    base_color = unreal.MaterialEditingLibrary.create_material_expression(
        material,
        unreal.MaterialExpressionConstant3Vector,
        -220,
        0,
    )
    base_color.set_editor_property("constant", color)
    unreal.MaterialEditingLibrary.connect_material_property(
        base_color,
        "",
        unreal.MaterialProperty.MP_BASE_COLOR,
    )

    roughness = unreal.MaterialEditingLibrary.create_material_expression(
        material,
        unreal.MaterialExpressionConstant,
        -220,
        120,
    )
    roughness.set_editor_property("r", 0.85)
    unreal.MaterialEditingLibrary.connect_material_property(
        roughness,
        "",
        unreal.MaterialProperty.MP_ROUGHNESS,
    )

    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def spawn(actor_class, name, location, rotation=None):
    actor = EDITOR_ACTOR_SUBSYSTEM.spawn_actor_from_class(
        actor_class,
        unreal.Vector(*location),
        rotation or unreal.Rotator(),
    )
    actor.set_actor_label(name)
    actor.tags = [unreal.Name("MazePrototype")]
    return actor


def cube(name, location, size, material=GREY_MATERIAL, collision=True):
    actor = spawn(unreal.StaticMeshActor, name, location)
    component = actor.static_mesh_component
    component.set_static_mesh(CUBE)
    component.set_world_scale3d(
        unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0)
    )
    component.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    component.set_mobility(unreal.ComponentMobility.STATIC)
    if material:
        component.set_material(0, material)
    return actor


def wall(name, x, y, length, along_x=True):
    size = (
        (length, WALL_THICKNESS, WALL_HEIGHT)
        if along_x
        else (WALL_THICKNESS, length, WALL_HEIGHT)
    )
    return cube(name, (x, y, WALL_HEIGHT / 2.0), size, WALL_MATERIAL)


def marker(name, location, color, text=None):
    target = spawn(unreal.TargetPoint, name, location)
    if SHOW_DEBUG_LABELS:
        label = spawn(
            unreal.TextRenderActor,
            name + "_Label",
            (location[0], location[1], location[2] + 120.0),
            unreal.Rotator(90.0, 0.0, 0.0),
        )
        component = label.text_render
        component.set_text(text or name)
        component.set_text_render_color(color)
        component.set_world_size(70.0)
    return target


def zone(name, location, extent, color):
    trigger = spawn(unreal.TriggerBox, name, location)
    trigger.set_actor_scale3d(
        unreal.Vector(extent[0] / 100.0, extent[1] / 100.0, extent[2] / 100.0)
    )
    if SHOW_DEBUG_LABELS:
        marker(name + "_Debug", (location[0], location[1], 10.0), color, name)
    return trigger


def clear_or_create_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
        for actor in EDITOR_ACTOR_SUBSYSTEM.get_all_level_actors():
            if unreal.Name("MazePrototype") in actor.tags:
                EDITOR_ACTOR_SUBSYSTEM.destroy_actor(actor)
    else:
        unreal.EditorLevelLibrary.new_level(MAP_PATH)


def build():
    global WALL_MATERIAL

    clear_or_create_level()

    WALL_MATERIAL = color_material(
        "M_Maze_WallGrey", unreal.LinearColor(0.32, 0.35, 0.40, 1.0)
    )
    floor_material = color_material(
        "M_Maze_FloorDark", unreal.LinearColor(0.08, 0.09, 0.11, 1.0)
    )
    room_a_material = color_material(
        "M_Maze_RoomA_Blue", unreal.LinearColor(0.05, 0.30, 0.80, 1.0)
    )
    room_b_material = color_material(
        "M_Maze_RoomB_Orange", unreal.LinearColor(0.90, 0.25, 0.04, 1.0)
    )
    room_c_material = color_material(
        "M_Maze_RoomC_Green", unreal.LinearColor(0.04, 0.60, 0.18, 1.0)
    )
    junction_material = color_material(
        "M_Maze_Junction_Yellow", unreal.LinearColor(0.85, 0.65, 0.03, 1.0)
    )

    # One continuous 5200 x 4600 floor. Coordinates: north is +Y.
    cube(
        "Maze_Floor",
        (0.0, 0.0, -FLOOR_THICKNESS / 2.0),
        (5200.0, 4600.0, FLOOR_THICKNESS),
        floor_material,
    )

    # Thin, non-colliding color pads distinguish research areas without
    # affecting character movement or NavMesh generation.
    cube("RoomA_ColorPad", (-1900, 1600, 1), (780, 680, 2), room_a_material, False)
    cube("RoomB_ColorPad", (1900, 1650, 1), (680, 580, 2), room_b_material, False)
    cube("RoomC_ColorPad", (1900, -1500, 1), (780, 680, 2), room_c_material, False)
    cube("Junction_ColorPad", (0, 0, 1), (1100, 1000, 2), junction_material, False)

    # Outer perimeter, with generous playable clearance.
    wall("Wall_South", 0, -2300, 5200, True)
    wall("Wall_North", 0, 2300, 5200, True)
    wall("Wall_West", -2600, 0, 4600, False)
    wall("Wall_East", 2600, 0, 4600, False)

    # Northwest Room A (about 800 x 700), open south and east approaches.
    wall("RoomA_North", -1900, 1950, 800, True)
    wall("RoomA_West", -2300, 1600, 700, False)
    wall("RoomA_SouthWest", -2150, 1250, 300, True)
    wall("RoomA_SouthEast", -1650, 1250, 300, True)
    wall("RoomA_EastNorth", -1500, 1800, 300, False)
    wall("RoomA_EastSouth", -1500, 1400, 200, False)
    cube(
        "RoomA_CentralObstacle",
        (-1900, 1600, 175),
        (350, 280, 350),
        room_a_material,
    )

    # Northeast Room B (about 700 x 600): narrow west gap, wide south route.
    wall("RoomB_North", 1900, 1950, 700, True)
    wall("RoomB_East", 2250, 1650, 600, False)
    wall("RoomB_WestNorth", 1550, 1850, 200, False)
    wall("RoomB_WestSouth", 1550, 1450, 200, False)
    wall("RoomB_SouthEast", 2075, 1350, 350, True)
    wall("RoomB_LShape_A", 1900, 1650, 350, True)
    wall("RoomB_LShape_B", 2075, 1500, 300, False)

    # Southeast Room C (about 800 x 700), exits to north and west.
    wall("RoomC_South", 1900, -1850, 800, True)
    wall("RoomC_East", 2300, -1500, 700, False)
    wall("RoomC_NorthWest", 1650, -1150, 300, True)
    wall("RoomC_NorthEast", 2150, -1150, 300, True)
    wall("RoomC_WestNorth", 1500, -1300, 300, False)
    wall("RoomC_WestSouth", 1500, -1700, 200, False)
    cube(
        "RoomC_CentralObstacle",
        (1900, -1500, 175),
        (350, 300, 350),
        room_c_material,
    )

    # Central and wing dividers produce several interconnected loops. Every
    # wall has generous clearance around both ends for the default Character.
    wall("Junction_SouthBlock", 0, -650, 800, True)
    wall("Junction_NorthBlock", 0, 650, 800, True)
    wall("West_RouteDivider", -750, 0, 1100, False)
    wall("East_RouteDivider", 750, 0, 1100, False)
    wall("Northwest_CrossRoute", -950, 1050, 700, True)
    wall("Northeast_CrossRoute", 950, 1050, 700, True)
    wall("WestWing_UpperDivider", -1750, 650, 750, True)
    wall("WestWing_LowerDivider", -1750, -600, 750, True)
    wall("EastWing_MidDivider", 1500, 500, 900, False)
    wall("EastWing_LowerDivider", 1450, -650, 850, True)
    wall("Southwest_Island_A", -1500, -1450, 650, True)
    wall("Southwest_Island_B", -1175, -1600, 300, False)
    wall("South_CenterDivider_West", -700, -1450, 500, False)
    wall("South_CenterDivider_East", 700, -1450, 500, False)
    wall("Seeker_Start_Screen", 0, -1850, 700, True)

    # Named research zones. Trigger extents remain clear of walls.
    zone("Room_A", (-1900, 1600, 100), (400, 350, 100), unreal.Color(80, 180, 255))
    zone("Room_B", (1900, 1650, 100), (350, 300, 100), unreal.Color(255, 170, 60))
    zone("Room_C", (1900, -1500, 100), (400, 350, 100), unreal.Color(100, 230, 120))
    zone("Central_Junction", (0, 0, 100), (550, 500, 100), unreal.Color(255, 255, 80))
    zone("Seeker_Start", (0, -2050, 100), (300, 250, 100), unreal.Color(255, 80, 80))

    player_start = spawn(unreal.PlayerStart, "Hider_PlayerStart", (-2050, 1750, 100))
    player_start.set_actor_rotation(unreal.Rotator(0, -90, 0), False)
    marker("Seeker_Spawn", (0, -2050, 100), unreal.Color(255, 50, 50))
    marker("HidingSpot_A", (-2100, 1800, 50), unreal.Color(80, 180, 255))
    marker("HidingSpot_B", (2100, 1800, 50), unreal.Color(255, 170, 60))
    marker("HidingSpot_C", (2100, -1700, 50), unreal.Color(100, 230, 120))
    if SHOW_DEBUG_LABELS:
        marker("Hider_Start_Debug", (-2050, 1750, 100), unreal.Color(80, 255, 255), "HIDER START")

    nav = spawn(unreal.NavMeshBoundsVolume, "Maze_NavMeshBounds", (0, 0, 200))
    nav.set_actor_scale3d(unreal.Vector(26.0, 23.0, 4.0))

    sun = spawn(
        unreal.DirectionalLight,
        "Maze_DirectionalLight",
        (0, 0, 1000),
        unreal.Rotator(-55, -35, 0),
    )
    sun_component = sun.get_component_by_class(
        unreal.DirectionalLightComponent
    )
    if sun_component:
        sun_component.set_intensity(5.0)
        sun_component.set_editor_property("atmosphere_sun_light", True)

    # Outdoor sky; the maze intentionally has no ceiling or roof.
    spawn(unreal.SkyAtmosphere, "Maze_SkyAtmosphere", (0, 0, 0))

    sky = spawn(unreal.SkyLight, "Maze_SkyLight", (0, 0, 800))
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    if sky_component:
        sky_component.set_intensity(1.0)
        sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(
        "Maze Hunt prototype generated at {} (minimum corridor width: {} uu).".format(
            MAP_PATH, CORRIDOR_WIDTH
        )
    )


build()
