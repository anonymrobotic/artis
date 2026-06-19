from artis_gripper import ArtisGripper


def main():
    with ArtisGripper("configs/artis_default.yaml") as g:
        print("ARTiS keyboard control")
        print("Commands: read, jam_on, jam_off, torque_off, torque_on, preset name, q")
        while True:
            cmd = input("> ").strip()
            if cmd in {"q", "quit", "exit"}:
                break
            elif cmd == "read":
                print("ticks:", g.read_joint_ticks())
                print("angles:", g.read_joint_angles())
                print("jammed:", g.read_jamming_state())
            elif cmd == "jam_on":
                g.jam_on()
            elif cmd == "jam_off":
                g.jam_off()
            elif cmd == "torque_off":
                g.enable_torque(False)
            elif cmd == "torque_on":
                g.enable_torque(True)
            else:
                g.apply_preset(cmd)


if __name__ == "__main__":
    main()
