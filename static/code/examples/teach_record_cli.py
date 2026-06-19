import argparse
from datetime import datetime

from artis_gripper import ArtisGripper, TeachingRecorder


def main():
    parser = argparse.ArgumentParser(description="Record ARTiS teaching steps")
    parser.add_argument("--config", default="configs/artis_default.yaml")
    parser.add_argument("--name", default="tool_sequence")
    parser.add_argument("--tool", default="unknown_tool")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    out = args.output or f"teaching_sequences/{args.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with ArtisGripper(args.config) as g:
        rec = TeachingRecorder(g, args.name, tool_type=args.tool)
        print("Commands:")
        print("  torque_off  - disable torque for manual positioning")
        print("  torque_on   - enable torque before recording or playback")
        print("  record NAME - save current joint ticks, joint angles, jamming state")
        print("  jam_on / jam_off")
        print("  read")
        print("  save")
        print("  quit")
        while True:
            cmd = input("teach> ").strip()
            if cmd in {"quit", "q", "exit"}:
                break
            if cmd == "torque_off":
                g.enable_torque(False)
            elif cmd == "torque_on":
                g.enable_torque(True)
            elif cmd == "jam_on":
                g.jam_on()
            elif cmd == "jam_off":
                g.jam_off()
            elif cmd == "read":
                print(g.read_joint_ticks())
            elif cmd.startswith("record"):
                parts = cmd.split(maxsplit=1)
                name = parts[1] if len(parts) > 1 else f"step_{len(rec.sequence.steps):03d}"
                step = rec.record_step(name)
                print("recorded:", step["name"], step["joint_ticks"], "jammed=", step["jamming"])
            elif cmd == "save":
                rec.save(out)
                print("saved", out)
            else:
                print("unknown command")

        rec.save(out)
        print("saved", out)


if __name__ == "__main__":
    main()
