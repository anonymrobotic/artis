# ARTiS motor mapping

This file records the motor numbering convention used by the mechanical design and the Dynamixel IDs used by the Python and ROS 2 API.

| Design motor | Kinematic joint | Programming ID | Function |
|---:|---|---:|---|
| Motor 1 | J0 | 8 | base rotation about the gripper axis; symmetrically rotates the two movable finger branches |
| Motor 2 | J1 | 1 | center finger-axis orientation |
| Motor 4 | J2 | 2 | left finger-axis orientation |
| Motor 6 | J3 | 3 | right finger-axis orientation |
| Motor 3 | J4 | 4 | center four-bar finger mechanism |
| Motor 5 | J5 | 5 | left four-bar finger mechanism |
| Motor 7 | J6 | 6 | right four-bar finger mechanism |

In code, command joints by semantic names such as `j0_base` or `j4_center_4bar`; do not hard-code raw IDs in experiments unless necessary.
