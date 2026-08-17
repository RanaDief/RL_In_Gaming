# Maze Hunt: Reinforcement Learning vs. Rule-Based NPC Behavior

A controlled 3D hide-and-seek game built with **Unreal Engine** to study and compare a traditional rule-based NPC with a **Reinforcement Learning (RL) NPC** trained through **AMD Schola** and **Proximal Policy Optimization (PPO)**.

Maze Hunt is a research prototype rather than a commercial game. Both NPC variants operate in the same environment with equivalent capabilities and information, enabling an objective comparison of their search behaviour.

## Overview

The player acts as the hider while a seeker NPC attempts to find and catch them before the round timer expires. The project implements two seeker variants:

- **Rule-Based Seeker** — controlled through predefined states and decision logic.
- **RL Seeker** — learns movement and search behaviour through reinforcement learning with AMD Schola and PPO.

### Research Question

> How does the search behaviour of an RL-trained seeker differ from that of a rule-based seeker in a small, partially observable 3D hide-and-seek maze?

## Key Features

- 3D hide-and-seek environment in Unreal Engine
- Rule-based seeker AI and PPO-trained RL seeker
- Partially observable environment with raycast sensing
- Player visibility, last-known-position, and sound-clue information
- Scripted hider behaviours for automated experiments
- Automated episode resets and CSV gameplay logging
- Controlled behavioural comparison and automated evaluation

## Technology Stack

| Component | Technology |
| --- | --- |
| Game engine | Unreal Engine 5.8 |
| RL framework | AMD Schola |
| RL algorithm / backend | PPO / Stable-Baselines3 |
| Training and analysis | Python |
| Environment sensing | Raycasts and game-state observations |
| Data logging | CSV |
| Target platform | Windows PC |

## Architecture

```text
Unreal Engine maze
  ├─ Player / hider, seeker NPCs, sensors, rewards, episode management, logging
  └─ AMD Schola
       └─ Python training pipeline (Stable-Baselines3 + PPO)
            └─ trained policy → Unreal RL seeker inference
```

AMD Schola bridges the Unreal environment and the Python reinforcement-learning pipeline.

## NPC Implementations

### Rule-Based Seeker

The baseline seeker uses manually programmed behaviour states:

```text
Patrol → Investigate sound / Chase visible player → Last known position → Local search → Patrol
```

It is intended to be consistent, easy to debug, predictable, and deterministic under the same conditions, though potentially repetitive in its search patterns.

### Reinforcement-Learning Seeker

The RL seeker learns a policy through repeated interaction with the maze rather than using specified patrol routes or search locations. It can move forward/backward, rotate, react to observations, visibility, and sound clues. It cannot teleport, jump, sprint, open doors, attack, or receive the exact hidden-player position.

## Reinforcement Learning Setup

The seeker NPC is the RL agent; the Unreal maze and hider form the training environment. Each episode is one hide-and-seek round.

### Observations

The agent may receive:

- Wall distance and raycast-hit information
- Player visibility, direction, and distance when visible
- Direction to the last known player position and time since last seen
- Direction, distance, and age of the latest sound clue
- Seeker velocity, rotation, and remaining round time

When the hider is hidden, the agent does not receive their exact position. Approximately eight directional raycasts (front, back, left, right, and diagonals) detect walls, the player, or empty space.

### Actions

The RL agent uses continuous movement and rotation actions:

```text
Movement ∈ [-1, 1]
Rotation ∈ [-1, 1]
```

The exact mapping is defined by the Unreal agent implementation.

### Reward Function

| Event | Reward |
| --- | ---: |
| Catch player | +10 |
| Player survives to timeout | -10 |
| Invalid episode / seeker stuck | -2 |
| See player | +0.2 |
| Reach last known player position | +0.1 |
| Enter an unvisited room | +0.05 |
| Hit wall / remain stationary | -0.05 |
| Repeatedly move into obstacle | -0.1 |

Small shaping rewards encourage movement toward a visible player or sound clue. Small time-step, repeated-area, and inefficient-movement penalties discourage unproductive behaviour. Reward values are experimental parameters, but the capture reward should remain much larger than shaping rewards.

## Hider Behaviours

Training progresses from simple to more difficult scripted hiders:

- **Stationary:** selects a room and stays there.
- **Fixed-route:** follows a predetermined route.
- **Random-room:** randomly selects rooms.
- **Moving:** changes rooms when the seeker approaches.
- **Random:** uses randomized movement and hiding decisions.

## Sound-Clue System

While the player is hidden, the seeker receives an approximate sound event roughly every five seconds: general direction, approximate distance, and sound age. The rule-based and RL seekers receive the same information to keep comparisons fair.

## Game Loop

```text
Start round → 10-second preparation → hider chooses a location → seeker released
→ 30-second search → player caught or timer expires → record data → reset episode
```

## Experimental Design

The independent variable is NPC decision-making method: rule-based control versus reinforcement-learning control. Key dependent variables include capture rate and time, player survival time, route diversity, repeated room visits, search efficiency, collisions, lost-player events, and generalization to new hider behaviours.

To isolate this difference, both NPCs use the same maze, speeds, capture distance, starting location, vision range, raycasts, sound clues, round timer, collision size, hider behaviour, and test conditions.

Planned scenarios include stationary, repeated-location, alternating-location, moving, and random hiders. The target experiment is 30 episodes × 5 hider behaviours × 2 NPC conditions = **300 episodes**.

## Data Collection and Metrics

Episodes are exported to CSV for analysis in Python or spreadsheet tools. Example fields include the episode and NPC type, training checkpoint, hider type, seed, result, capture time, travelled distance, wall collisions, room visits, stationary time, player sightings, chase/search time, and final minimum distance.

```csv
Episode,NPCType,HiderType,Result,CaptureTime,WallCollisions,RoomsVisited
1,RuleBased,Stationary,Caught,12.4,1,3
2,RL,Stationary,Caught,9.7,2,2
3,RuleBased,Moving,Escaped,30.0,0,4
```

```text
Search efficiency = successful captures / average capture time
Repetition rate   = repeated room visits / total room visits
Collision rate    = wall collisions / episode duration
```

Generalization is assessed against hider behaviours not used during training, such as training against a stationary hider and testing against a moving hider.

## Requirements

- Unreal Engine **5.8**
- Windows
- Visual Studio with C++ game-development tools (needed if Unreal prompts you to build the Schola plugin)

## Open the Project

From PowerShell, run:

```powershell
Start-Process ".\RL_In_Gaming\RL_In_Gaming.uproject"
```

Or double-click `RL_In_Gaming/RL_In_Gaming.uproject` in File Explorer.

If Unreal asks to rebuild modules or compile the plugin, choose **Yes** and let the build finish before opening the level.

## Run the Maze

1. In Unreal's Content Browser, open `Content/MazeHunt`.
2. Double-click `MazePrototype` to load the maze level.
3. Click the **Play** button in the toolbar to run it.

## Project Layout

```
RL_In_Gaming/
|- Config/                  # Unreal Engine project configuration
|- Content/MazeHunt/        # Maze level and its materials
|- Plugins/Schola/          # Reinforcement-learning integration plugin
`- RL_In_Gaming.uproject    # Unreal project entry point
```

## Notes

- Unreal-generated folders such as `Saved`, `Intermediate`, and `DerivedDataCache` are excluded from version control.
- Schola has its own documentation at `RL_In_Gaming/Plugins/Schola/README.md`.

## Training Workflow

```text
Start Unreal environment → initialize Schola agent → define observations, actions, and rewards
→ start PPO training → save checkpoints → evaluate policies → export gameplay data → analyse results
```

Begin with a simple environment and progressively introduce more challenging hider behaviours. Inference uses a selected PPO checkpoint through AMD Schola to control the RL seeker in Unreal gameplay.

## Development Modes

- **Manual play:** a human controls the hider.
- **Automated experiment:** a scripted hider plays against the seeker and produces data.
- **Training:** the RL seeker interacts through AMD Schola while PPO runs from Python.

## Research Goals

The project examines whether the RL seeker finds the player faster, captures more often, uses more diverse routes, repeats areas less, handles moving hiders better, generalizes beyond training, or is less predictable than the baseline. It does not assume that RL will outperform rule-based AI: better baseline efficiency or reliability is also a valid finding.

## Minimum Viable Product

- [x] Fixed maze environment
- [ ] Player/hider system
- [ ] Rule-based seeker
- [ ] RL seeker and AMD Schola integration
- [ ] PPO training
- [ ] Sound clues, timer, and capture detection
- [ ] Automated resets and CSV logging
- [ ] At least three hider behaviours
- [ ] Direct NPC comparison

The core goal is to observe, measure, and compare behavioural differences.

## Team

- **Rana:** RL training and evaluation — Schola integration, observations, actions, rewards, PPO, checkpoints, and data analysis.
- **Donia:** Unreal and game systems — maze, player controls, rule-based AI, rounds, capture, UI, logging, and presentation footage.
- **Shared:** experimental design, testing, reward tuning, research writing, final evaluation, and presentation.

## Project Status

Current focus: integrating AMD Schola with the Unreal Engine environment and training the RL seeker with PPO. The project is being developed as a research prototype for evaluating reinforcement-learning NPC behaviour against a traditional rule-based baseline.

## License

This project is licensed under the [MIT License](LICENSE).
