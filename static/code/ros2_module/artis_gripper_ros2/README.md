# ARTiS ROS 2 module

This package exposes the ARTiS gripper through ROS 2 topics and services.

## Topics

- `~/joint_command_ticks` (`sensor_msgs/JointState`): command Dynamixel goal positions in raw ticks. Use joint names from `configs/artis_default.yaml`.
- `~/joint_states` (`sensor_msgs/JointState`): published raw encoder ticks.
- `~/preset` (`std_msgs/String`): apply a named preset such as `z`, `x`, `a`, `b`, etc.
- `~/jamming` (`std_msgs/Bool`): turn the jamming palm on/off.

## Services

- `~/set_jamming` (`std_srvs/SetBool`)
- `~/torque_enable` (`std_srvs/Trigger`)
- `~/torque_disable` (`std_srvs/Trigger`)

## Build

```bash
cd ~/artis_ws/src
git clone <your-artis-repo-url> ARTiS_Gripper_API
cd ARTiS_Gripper_API
pip install -e .
cd ~/artis_ws
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 run artis_gripper_ros2 artis_node --ros-args -p config:=/absolute/path/to/artis_default.yaml
ros2 topic pub /artis_gripper/preset std_msgs/msg/String "{data: z}" --once
ros2 service call /artis_gripper/set_jamming std_srvs/srv/SetBool "{data: true}"
```
