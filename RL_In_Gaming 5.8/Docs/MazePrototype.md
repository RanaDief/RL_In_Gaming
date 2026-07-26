# Maze Hunt greybox prototype

The prototype is generated rather than stored as a binary map. Its source is
`Content/Python/build_maze_prototype.py`. It creates `/Game/MazeHunt/MazePrototype`
with a single floor, 350-unit walls, broad corridors, multiple route loops, named
research zones, separate starts, three hiding spots, lighting, and a full-map
navigation bounds volume.

## Generate or regenerate

1. Open `RL_In_Gaming.uproject` in Unreal Editor 5.8 and restart if prompted after
   the Python Editor Script Plugin is enabled.
2. Open **Window > Output Log** and switch the command input from `Cmd` to `Python`.
3. Run:

   ```python
   exec(open(unreal.Paths.project_content_dir() + "Python/build_maze_prototype.py").read())
   ```

4. Open `/Game/MazeHunt/MazePrototype`. The script saves the level automatically.
   Running it again safely replaces actors tagged `MazePrototype`.
5. If desired, set this map in **Project Settings > Maps & Modes**. The generator
   deliberately does not replace the existing First Person startup map or game mode.

Set `SHOW_DEBUG_LABELS = False` near the top of the script and regenerate to hide
the room, spawn, and hiding-spot labels. Wall height, thickness, corridor width,
and floor thickness are also defined there.

## Validate

- Press **P** in the level viewport. Green navigation overlay should cover every
  room, both sides of the central junction, and all connecting corridors.
- If green does not appear immediately, use **Build > Build Paths** or move the
  `Maze_NavMeshBounds` volume slightly to request a rebuild.
- Play in Editor with the existing First Person game mode and walk both route
  sequences to each room. Confirm all cubes block movement and sight lines.
- Confirm the World Outliner contains `Room_A`, `Room_B`, `Room_C`,
  `Central_Junction`, `Seeker_Start`, `Hider_PlayerStart`, `Seeker_Spawn`, and
  `HidingSpot_A` through `HidingSpot_C`.

The generated `.umap` is intentionally not committed by the script. Generate and
visually inspect it in the target engine build because Unreal Editor Python APIs
and navmesh baking cannot be fully validated without launching Unreal Editor.
