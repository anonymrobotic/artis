from __future__ import annotations

import argparse

from .artis_gripper import ArtisGripper


def main():
    parser = argparse.ArgumentParser(description="ARTiS gripper keyboard CLI")
    parser.add_argument("--config", default="configs/artis_default.yaml")
    args = parser.parse_args()

    with ArtisGripper(args.config) as g:
        print("Commands: preset name, jam_on, jam_off, read, torque_off, torque_on, quit")
        while True:
            cmd = input("artis> ").strip()
            if cmd in {"q", "quit", "exit"}:
                break
            if cmd == "jam_on":
                g.jam_on()
            elif cmd == "jam_off":
                g.jam_off()
            elif cmd == "read":
                print(g.read_joint_ticks())
            elif cmd == "torque_off":
                g.enable_torque(False)
            elif cmd == "torque_on":
                g.enable_torque(True)
            else:
                g.apply_preset(cmd)


if __name__ == "__main__":
    main()
