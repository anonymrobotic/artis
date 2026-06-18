from __future__ import annotations

import argparse
from pathlib import Path

from .artis_gripper import ArtisGripper


def main() -> None:
    parser = argparse.ArgumentParser(description="ARTiS gripper command-line controller")
    parser.add_argument("--config", default="configs/artis_default.yaml", help="Path to YAML config")
    args = parser.parse_args()

    cfg = Path(args.config)
    print(f"Loading ARTiS config: {cfg}")
    print("Commands: preset name/key, on, off, read, torque_on, torque_off, exit")

    with ArtisGripper(cfg) as gripper:
        while True:
            cmd = input("ARTiS> ").strip()
            if cmd in {"exit", "quit", "e"}:
                break
            if cmd in {"on", "jam_on", "q"}:
                gripper.jam_on()
                print("Jamming palm ON")
            elif cmd in {"off", "jam_off", "w"}:
                gripper.jam_off()
                print("Jamming palm OFF")
            elif cmd == "read":
                print(gripper.read_joint_ticks())
            elif cmd == "torque_on":
                gripper.enable_torque(True)
            elif cmd == "torque_off":
                gripper.enable_torque(False)
            elif cmd:
                gripper.apply_preset(cmd)
                print(f"Applied preset: {cmd}")


if __name__ == "__main__":
    main()
