# ARTiS Gripper API

Python and ROS 2 control interface for the ARTiS adaptive robotic gripper.

ARTiS combines:

- a central jamming palm controlled through an Arduino relay,
- seven Dynamixel actuators connected through U2D2,
- two finger rotation around gripper axis joint `J0`,
- three finger-axis orientation joints `J1-J3`,
- three four-bar finger mechanisms `J4-J6`.

This repository have a standalone Python API, a ROS 2 module, example scripts, configuration files, and utility firmware for the microcontroller.

## Repository structure

```text
artis_gripper_api/
├── artis_gripper/                 # Python API
│   ├── artis_gripper.py            # high-level gripper class
│   ├── dynamixel_bus.py            # MX-series Dynamixel Protocol 1.0 wrapper
│   ├── arduino_palm.py             # jamming-palm serial interface
│   ├── kinematics.py               # four-bar mechanism helper
│   └── cli.py                      # command-line controller
├── configs/
│   └── artis_default.yaml          # motor IDs, limits, ports, presets
├── examples/
│   ├── keyboard_control.py
│   └── simple_demo.py
├── arduino/
│   └── Arduino_communication.ino   # relay firmware for palm jamming
└── ros2_module/
    └── artis_gripper_ros2/         # ROS 2 Python package
```

## Hardware mapping

Default mapping follows the ARTiS mechanical design motor labels and the Dynamixel IDs used for programming:

| Design motor | Joint | Mechanical meaning | Dynamixel ID |
|---:|---|---|---:|
| Motor 1 | `J0` / `j0_base` | fingers symmetric rotation around gripper axis | 8 |
| Motor 2 | `J1` / `j1_center_axis` | center finger-axis orientation | 1 |
| Motor 4 | `J2` / `j2_left_axis` | left finger-axis orientation | 2 |
| Motor 6 | `J3` / `j3_right_axis` | right finger-axis orientation | 3 |
| Motor 3 | `J4` / `j4_center_4bar` | center four-bar finger mechanism | 4 |
| Motor 5 | `J5` / `j5_left_4bar` | left four-bar finger mechanism | 5 |
| Motor 7 | `J6` / `j6_right_4bar` | right four-bar finger mechanism | 6 |

Edit `configs/artis_default.yaml` if your actual IDs differ. The API commands joints by semantic names, while the YAML maps those names to Dynamixel IDs.

## Installation

```bash
git clone <your-repo-url> ARTiS_Gripper_API
cd ARTiS_Gripper_API
python3 -m pip install -e .
```

On Ubuntu, use a persistent Dynamixel port when possible:

```bash
ls /dev/serial/by-id/
sudo chmod 666 /dev/serial/by-id/<your-u2d2-id>
```

Then update:

```yaml
serial:
  dynamixel_port: /dev/serial/by-id/<your-u2d2-id>
  arduino_port: /dev/ttyACM0
```

## Python quick start

```python
from artis_gripper import ArtisGripper

with ArtisGripper("configs/artis_default.yaml") as g:
    g.apply_preset("z")       # center base / open reference posture
    g.jam_on()                # activate palm jamming
    print(g.read_joint_ticks())
    g.jam_off()
```

Keyboard-style control:

```bash
python examples/keyboard_control.py
```

CLI control:

```bash
artis-cli --config configs/artis_default.yaml
```

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
```

Run the node:

```bash
ros2 run artis_gripper_ros2 artis_node --ros-args -p config:=/absolute/path/to/configs/artis_default.yaml
```

Apply a preset:

```bash
ros2 topic pub /artis_gripper/preset std_msgs/msg/String "{data: z}" --once
```

Control the palm:

```bash
ros2 service call /artis_gripper/set_jamming std_srvs/srv/SetBool "{data: true}"
ros2 service call /artis_gripper/set_jamming std_srvs/srv/SetBool "{data: false}"
```

Command raw Dynamixel ticks:

```bash
ros2 topic pub /artis_gripper/joint_command_ticks sensor_msgs/msg/JointState \
"{name: ['j0_base', 'j4_center_4bar'], position: [1712.0, 1330.0]}" --once
```

## Four-bar kinematics helper

`artis_gripper.kinematics.solve_fourbar()` implements the planar closure equation used in the ARTiS mechanism description:

```python
from math import radians
from artis_gripper import FourBarGeometry, solve_fourbar

geom = FourBarGeometry(l0=30, l1=25, l2=40, l3=35, theta0=0.0, r_tip=10, theta_tip=0.2)
result = solve_fourbar(radians(60), geom)
print(result)  # theta2, theta3, fingertip (x, y)
```

## Important safety notes

- Test each motor independently before applying full presets.
- Verify all motor IDs in Dynamixel Wizard config.
- Keep Dynamixel Wizard closed while running the API because the serial port can be locked by only one process.
- The relay logic in `arduino/Arduino_communication.ino` is explicit: `1 = jamming ON`, `0 = jamming OFF`. Set `RELAY_ACTIVE_LOW` according to your relay module.
- The legacy control script mixed two conventions: the enabled `DXL_IDs` list used `1,2,3,4,5,6,8`. The current repository follows the mechanical design mapping: `J1-J6 = ID 1-ID 6` and `J0 = ID 8`.

## Citation

If you use ARTiS Gripper in research, please cite:
```bibtex
@article{2026artisgripper,
  title={ARTiS: An Adaptive Robotic Gripper for Enhanced Tool Manipulation in Disassembly Applications},
  author={Mykhailyshyn, Roman and Domae, Yukiyasu and Harada, Kensuke},
  journal={TASE},
  year={2026}
}
