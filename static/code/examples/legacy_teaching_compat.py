"""Compatibility mode for the original teaching scripts.

Old behavior:
  t: read and hold orientation/base motors, turn jamming ON, close four-bar motors to 1000
  y: disable torque and turn jamming OFF for manual adjustment
  u: move to old reference posture and turn jamming OFF
"""

from artis_gripper import ArtisGripper


def main():
    with ArtisGripper("configs/artis_legacy_teaching.yaml") as g:
        print("Legacy ARTiS teaching commands: t, y, u, read, e")
        while True:
            key = input("legacy> ").strip().lower()
            if key == "t":
                saved = {j: g.read_joint_ticks()[j] for j in ["J1", "J2", "J3", "J0"]}
                print("Saved fixed joint ticks:", saved)
                g.jam_on()
                g.move_to_ticks(saved)
                g.apply_preset("legacy_t_fourbar_close")
            elif key == "y":
                g.enable_torque(False)
                g.jam_off()
                print("Torque disabled for manual adjustment.")
            elif key == "u":
                g.enable_torque(True)
                g.apply_preset("legacy_u")
            elif key == "read":
                print(g.read_joint_ticks())
            elif key == "e":
                break
            else:
                print("Unknown command")


if __name__ == "__main__":
    main()
