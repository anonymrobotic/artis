# ARTiS motor mapping

Current mapping from the design figure:

| Design motor | Joint | Meaning | Dynamixel ID |
|---:|---|---|---:|
| Motor 1 | `J0` | base rotation about gripper axis | 8 |
| Motor 2 | `J1` | center finger-axis orientation | 1 |
| Motor 4 | `J2` | left finger-axis orientation | 2 |
| Motor 6 | `J3` | right finger-axis orientation | 3 |
| Motor 3 | `J4` | center four-bar mechanism | 4 |
| Motor 5 | `J5` | left four-bar mechanism | 5 |
| Motor 7 | `J6` | right four-bar mechanism | 6 |

The legacy teaching scripts used a different experimental convention:

| Semantic joint | Legacy ID |
|---|---:|
| `J0` | 8 |
| `J1` | 2 |
| `J2` | 4 |
| `J3` | 6 |
| `J4` | 3 |
| `J5` | 5 |
| `J6` | 7 |

Use `configs/artis_default.yaml` for the current design mapping and `configs/artis_legacy_teaching.yaml` only for reproducing old experiments.
