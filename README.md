# Elden-Gym

A Gymnasium-compatible environment wrapper for Elden Ring, designed for training deep reinforcement learning agents.
This project utilizes screen capture and memory manipulation to
gather state information and reward information respectively.

<div align="center">

![](readme_src/er_nn_untrained.gif)

_Untrained agent on "one-shot" mode_

</div>

## Contents

- [Overview](#overview)
    - [Key-Features](#key-features)
    - [Environment Observations](#environment-observations)
    - [Getting Started](#getting-started)
- [Elden Ring API](#elden-ring-api)
- [Roadmap](#roadmap)
- [Known Issues and Limitations](#known-issues-and-limitations)
- [Credits and Inspirations](#credits-and-inspirations)
- [Troubleshooting](#troubleshooting)
- [Research and Results](#research-and-results)

## Overview

Elden-Gym provides a bridge between Elden Ring and Stable Baselines3, specifically sb3-contrib, due to the recurrentPPO policy that is available. Unlike other Elden Ring environments that use screen capture and pixel processing to determine reward information, this environment utilizes the memory of the game itself, similar to [SoulsGym](https://github.com/amacati/SoulsGym), which is also the main
inspiration for this project. However, unlike that project, this game does not use ground-truth state information and instead uses screen capture to increase generalizability of the agent.

#### Key-Features

- **Direct Memory Observation** - The environment interacts and views memory directly and has the memory offsets loaded so simple functions can be used to access values that correspond with the player and boss.
- **SB3 Ready** - Fully compatible with SB3 and SB3-contrib, which is what was used in the training process.

#### Environment Observations

<div align="center">

| Observation    | Box(0, 255, ((H, W, 1), 3), uint8) | Grayscale frame-buffer from game window                 |
| -------------- | ---------------------------------- | ------------------------------------------------------- |
| Action Space   | Dict                               | Movement: Box(-1, 1, (2,)) Buttons: Discrete(n)         |
| Reward Logic   | Memory-Driven                      | Changes in HP (Player & Boss), Stamina, and Flask count |
| Training Modes | int (0-2)                          | Terminal conditions: one-shot, 40% hp, 0% hp            |

</div>

#### Getting Started

**Requirements**

To use this environment, Elden Ring must be owned. Personally, I am using a copy from
Steam, and I do not condone piracy, so no support will be given to those with illegitimate copies of the game.

Next, [memory manipulation library](https://github.com/JSilvestrini/PyMym) being used currently only supports Windows x64 machines,
once I expand that library the project may be able to run on other OSs.

**Installation**

First, ensure that you have installed the [Elden Ring Boss Arena](https://www.nexusmods.com/eldenring/mods/5645?tab=files&file_id=31835) mod and followed its installation steps.
During the training process, Boss Arena (Sandbox 3.0) was the version used.

Secondly, this repository uses Python 3.12, so make sure that you have the correct version installed.

```bash
git clone https://github.com/JSilvestrini/Elden-Gym.git
cd Elden-Gym
python -m venv elden-gym
pip install -r requirements.txt
```

**Usage**

```bash
# Navigate to ./src/ and train
python run.py --total-timesteps 102400 # I prefer multiples of 1024
```

**Using the Environment**

```python
# The environment can be created like so
import er_environment as ee

# Training mode determines what 'done' function to use
# 0: If the agent gets hit once or if the agent wins, finish
# 1: If the agent's health is under 40% or if the agent wins, finish
# 2: If the agent's health reaches 0 or if the agent wins, finish
# n_steps needs to be the same as the policy's n_steps
    # to ensure that episodes line up correctly
env = ee.EldenRing(train_mode=2, n_steps=1024)

obs, info = env.reset()
for _ in range(1000):
    # Your agent logic here
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
```

---

## Elden Ring API

Included with the environment is a process wrapper that gives access to the Elden Ring internals. By using this API, custom reward functions, terminal conditions, and state information can be created.

```Python
import PyMym as pm
from backend.game_accessor import GameAccessor
import time

er = pm.ProcessWrapper(application_name="eldenring.exe")
game = GameAccessor(wrapper=er)

p_health = game.get_player_health()
e_health = game.get_enemy_health()

# After loading screens, check if this is above 0
# If not, then the current addresses are invalid
while not game.check_world_pointer():
    time.sleep(0.2)

...
```

The functions within the GameAccessor class focus on reading the game state rather than memory manipulation to ensure game stability. Write functionality may be added in future updates.

**NOTE:** When using the API, make sure that the WorldChrMan pointer is valid. The `check_world_pointer()` method must be used to validate the address state after loading screens.

---

## Roadmap

I plan to expand the environment to support the following encounters:

- **Base Game:** Crucible Knight, Morgott the Omen King, Elemer of the Briar, Godfrey, First Elden Lord.

- **Shadow of the Erdtree:** Rellana, Twin Moon Knight, Messmer the Impaler, Midra, Lord of Frenzied Flame.

Additionally, I intend to work on stability of the environment, reduce the amount of hard-coded time.sleep() calls, create video documentation of the agent's performance, and continue expanding the API.

---

## Known Issues and Limitations

- **Cutscenes:** When first developing the API and environment, it was difficult to determine if the agent was in a cutscene or not due to the cutscene flag becoming 'sticky' or failing to toggle. Currently I am working on a different way to determine if the agent is in a cutscene or loading state without relying on pixel processing.

- **Lock-on:** To minimize the action space, the environment currently forces the agent to lock on as soon as it enters the arena. For most bosses this is fine, but for large or mobile bosses this is an issue.

- **Multi-Enemy Fights:** While this was originally supported before the rewrite, the current lock-on constraints and simplified action space made maintaining this feature challenging. Once the action space is expanded to support lock-on and camera control this will be looked at again.

- **Ashes of War:** Currently these are not supported to keep the action space manageable. This may be revisited in the future once a multi-discrete action space is deemed manageable.

---

## Credits and Inspirations

The initial idea for this came from a [community discussion on Reddit](https://www.reddit.com/r/MachineLearning/comments/134r0xf/p_soulsgym_beating_dark_souls_iii_bosses_with/), which led me to the [SoulsGym repository](https://github.com/amacati/SoulsGym). While researching Elden Ring environments afterwards, I noticed that none of them utilized memory access for the creation of reward functions like **SoulsGym**. Instead they used screenshots and checked pixels to determine boss and player health, which I found to be inefficient and prone to errors. Thus, Elden-Gym was created.

**Acknowledgments**

- **[SoulsGym](https://github.com/amacati/SoulsGym):** The `speedhack.py` and corresponding `.dll` were both adapted from this project. Their work on the Dark Souls 3 environment was the foundation for this environment.

- **[The Grand Archives](https://github.com/The-Grand-Archives/Elden-Ring-CT-TGA) & [Elden Ring FPS](https://github.com/Dasaav-dsv/erfps/tree/master):** These resources contained information about the byte patterns and pointer chains that were needed to locate state information for the environment.

- **[Elden Ring Boss Arena](https://www.nexusmods.com/eldenring/mods/5645?tab=files&file_id=31835):** This mod was essential in streamlining the training process by allowing instant boss resets and menu-based boss navigation rather than boss runs.

---

## Troubleshooting

- **EAC & Versions:** Ensure that you are using **[Elden Ring Boss Arena](https://www.nexusmods.com/eldenring/mods/5645?tab=files&file_id=31835) version 3.0**. This mod should disable Easy Anti-Cheat, which is required for the API to access game memory.

- **Environment:** Verified on **Python 3.12**.

- **Hardware Acceleration:** This project utilizes **PyTorch with CUDA 13**. If you use a different version of CUDA, be sure to modify `requirements.txt` accordingly.

- **Display:** The game must be running in windowed or borderless windowed mode for the screen capture observation space.

---

## Research and Results

_Currently in progress_

The agent is training using the Recurrent PPO algorithm (from sb3-contrib) using a CNNLSTM policy architecture.
The goal is to test if an agent using screen capture and LSTM can out-generalize the SoulsGym baseline that only uses ground-truth state information. My belief is that it will, and that using a LSTM policy will have the agent perform better than just using frame stacking since the environment is complex. See [here](https://github.com/seoboseung/24KoreaAIconf).

Initial training is focused on the current bosses:

- Soldier of Godrick
- Beastman of Farum Azula
- Scaly Misbegotten
