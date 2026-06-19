# ARTiS Gripper API

Python and ROS 2 control interface for the ARTiS adaptive robotic gripper.

ARTiS combines:

- a central jamming palm controlled through an Arduino relay,
- seven Dynamixel MX actuators connected through U2D2,
- one base rotation joint `J0`,
- three finger-axis orientation joints `J1-J3`,
- three four-bar finger mechanisms `J4-J6`,
- optional teaching buttons for recording manually demonstrated gripper sequences.

The repository is organized as a hardware abstraction layer, a teaching/replay layer, and a ROS 2 integration layer.

## Repository structure

```text
artis_gripper_api/
├── artis_gripper/                    # Python API
│   ├── artis_gripper.py               # high-level ARTiS class
│   ├── dynamixel_bus.py               # MX-series Protocol 1.0 wrapper
│   ├── arduino_palm.py                # jamming-palm and button serial interface
│   ├── teaching.py                    # teach-and-replay sequence recorder/player
│   ├── autonomous_controller.py       # sensor-guided control skeleton
│   ├── kinematics.py                  # four-bar kinematics helper
│   └── cli.py                         # terminal controller
├── configs/
│   ├── artis_default.yaml             # current design motor mapping
│   └── artis_legacy_teaching.yaml     # old experimental mapping
├── examples/
│   ├── keyboard_control.py
│   ├── teach_record_cli.py
│   ├── playback_sequence.py
│   ├── button_teaching.py
│   └── legacy_teaching_compat.py
├── arduino/
│   ├── Arduino_communication.ino
│   └── Arduino_com_teaching_button.ino
├── legacy/                            # original uploaded teaching scripts
├── docs/
│   ├── motor_mapping.md
│   └── teaching_mode.md
└── ros2_module/
    └── artis_gripper_ros2/
```

## Current motor mapping

| Design motor | Joint | Mechanical meaning | Programming ID |
|---:|---|---|---:|
| Motor 1 | `J0` | base rotation about gripper axis | 8 |
| Motor 2 | `J1` | center finger-axis orientation | 1 |
| Motor 4 | `J2` | left finger-axis orientation | 2 |
| Motor 6 | `J3` | right finger-axis orientation | 3 |
| Motor 3 | `J4` | center four-bar mechanism | 4 |
| Motor 5 | `J5` | left four-bar mechanism | 5 |
| Motor 7 | `J6` | right four-bar mechanism | 6 |

The uploaded old teaching code used the experimental list `[2, 3, 4, 5, 6, 7, 8]`; this is preserved separately in `configs/artis_legacy_teaching.yaml` and `legacy/`.

## Installation

```bash
git clone https://github.com/anonymrobotic/artis.git
cd artis/static/code/artis_gripper_api

python -m venv venv
source venv/bin/activate   # Linux
# or
venv\Scripts\activate      # Windows

pip install -r requirements.txt
pip install -e .
```

Required Python packages:

```bash
pip install dynamixel-sdk pyserial pyyaml
```

## Python quick start

```python
from artis_gripper import ArtisGripper

with ArtisGripper("configs/artis_default.yaml") as gripper:
    gripper.open_gripper()
    gripper.jam_on()
    print(g.read_joint_ticks())
    gripper.jam_off()
```

## Teaching mode

Record a manually demonstrated sequence:

```bash
python examples/teach_record_cli.py --config configs/artis_default.yaml --name screwdriver_grasp
python examples/playback_sequence.py teaching_sequences/screwdriver_grasp.json --config configs/artis_default.yaml
```

Typical teaching sequence:

```text
1. torque_off      # manually position the gripper
2. torque_on       # hold the current configuration
3. record open_or_preshape
4. jam_on / jam_off if required
5. record jammed_or_closed_state
6. save
```

Replay the sequence:

```bash
python examples/playback_sequence.py teaching_sequences/screwdriver_grasp_YYYYMMDD_HHMMSS.json --config configs/artis_default.yaml
```

Button-based teaching:

```bash
python examples/button_teaching.py --config configs/artis_default.yaml --name tool_grasp_button
```

Button serial messages:

| Message | Action |
|---|---|
| `15` | record current gripper state |
| `16` | toggle Dynamixel torque |
| `17` | save sequence and exit |

## Legacy teaching compatibility

The old scripts are stored under `legacy/`. Their behavior is also available through:

```bash
python examples/legacy_teaching_compat.py
```

Legacy keys:

```text
t = save selected current positions, jam palm, close four-bar motors
y = torque off and jam off for manual adjustment
u = return to reference posture and jam off
```

## Relay protocol

The new Arduino firmware uses:

```text
1 = JAM_ON
0 = JAM_OFF
? = print state
```

Set `RELAY_ACTIVE_LOW` in the Arduino firmware depending on the relay module. The original uploaded teaching-button firmware had an ambiguous/inverted comment convention, so the fixed firmware is recommended.

## ROS 2 quick start

```bash
mkdir -p ~/artis_ws/src
cd ~/artis_ws/src
git clone <your-repo-url> ARTiS_Gripper_API
cd ARTiS_Gripper_API
python3 -m pip install -e .
cd ~/artis_ws
colcon build --symlink-install
source install/setup.bash
ros2 run artis_gripper_ros2 artis_node --ros-args -p config:=/absolute/path/to/configs/artis_default.yaml
```

## Citation

If you use ARTiS Gripper in research, please cite:
```bibtex
@article{2026artisgripper,
  title={ARTiS: An Adaptive Robotic Gripper for Enhanced Tool Manipulation in Disassembly Applications},
  author={________},
  journal={TASE},
  year={2026}
}
