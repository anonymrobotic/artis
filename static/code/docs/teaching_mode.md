# ARTiS teaching mode

The teaching mode converts manually selected gripper poses into reusable ARTiS motion primitives.

## Legacy teaching behavior

The original teaching scripts used three core keyboard actions:

- `y`: disable Dynamixel torque and turn the palm relay off so a person can manually adjust the gripper.
- `t`: read and store the current positions of selected orientation/base motors, activate jamming, hold those motors at their measured positions, and close the four-bar motors to a fixed target.
- `u`: return the motors to a reference posture and turn jamming off.

The legacy scripts are preserved in `legacy/` and a compatibility implementation is provided in `examples/legacy_teaching_compat.py`.

## New teaching workflow

The new API stores a full sequence as JSON. Each step contains:

- semantic joint names `J0`-`J6`,
- raw Dynamixel ticks,
- converted joint angles in degrees,
- jamming-palm state,
- timing information,
- optional metadata.

Typical workflow:

```bash
python examples/teach_record_cli.py --config configs/artis_default.yaml --name screwdriver_grasp --tool screwdriver
```

Commands inside the teaching CLI:

```text
torque_off      disable torque for manual positioning
torque_on       enable torque before recording
record NAME     save current gripper state
jam_on          activate jamming palm
jam_off         release jamming palm
save            write the JSON sequence
quit            save and exit
```

Replay:

```bash
python examples/playback_sequence.py teaching_sequences/screwdriver_grasp_YYYYMMDD_HHMMSS.json --config configs/artis_default.yaml
```

## Button teaching

Upload `arduino/Arduino_com_teaching_button.ino` to the Arduino, then run:

```bash
python examples/button_teaching.py --config configs/artis_default.yaml --name tool_grasp_button
```

Button mapping:

| Arduino message | Meaning in Python |
|---|---|
| `15` | record current step |
| `16` | toggle Dynamixel torque |
| `17` | save sequence and exit |

## Important relay note

The uploaded legacy Arduino firmware had an inverted/ambiguous relay convention: setup wrote the relay pin HIGH while the comment said the relay was OFF, and the serial commands printed the opposite of the Python-side assumption. The new firmware makes the convention explicit:

```text
1 = JAM_ON
0 = JAM_OFF
```

Set `RELAY_ACTIVE_LOW` in the Arduino firmware and `palm.on_command` / `palm.off_command` in the YAML configuration according to your relay module.
