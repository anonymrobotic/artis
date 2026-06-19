"""Teaching mode controlled by Arduino buttons.

Expected serial lines from Arduino:
  15 -> record current step
  16 -> toggle torque on/off
  17 -> save and exit
"""

import argparse
from datetime import datetime

from artis_gripper import ArtisGripper, TeachingRecorder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/artis_default.yaml")
    parser.add_argument("--name", default="button_teaching")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    out = args.output or f"teaching_sequences/{args.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    torque_enabled = True

    with ArtisGripper(args.config) as g:
        rec = TeachingRecorder(g, args.name)
        print("Waiting for Arduino button serial messages: 15=record, 16=torque toggle, 17=save+exit")
        while True:
            line = g.read_button_line()
            if not line:
                continue
            if line == "15":
                step = rec.record_step(f"button_step_{len(rec.sequence.steps):03d}")
                print("recorded", step["name"], step["joint_ticks"])
            elif line == "16":
                torque_enabled = not torque_enabled
                g.enable_torque(torque_enabled)
                print("torque", "enabled" if torque_enabled else "disabled")
            elif line == "17":
                rec.save(out)
                print("saved", out)
                break
            else:
                print("Arduino:", line)


if __name__ == "__main__":
    main()
