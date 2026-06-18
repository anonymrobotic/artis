from pathlib import Path

from artis_gripper import ArtisGripper

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "artis_default.yaml"

print("ARTiS keyboard control")
print("Preset keys: a s d f z x c b n m")
print("Palm: q=jam ON, w=jam OFF")
print("Other: r=read positions, e=exit")

with ArtisGripper(CONFIG) as gripper:
    while True:
        key = input("Command: ").strip().lower()
        if key == "e":
            break
        if key == "q":
            gripper.jam_on()
            print("Jamming palm ON")
        elif key == "w":
            gripper.jam_off()
            print("Jamming palm OFF")
        elif key == "r":
            print(gripper.read_joint_ticks())
        elif key:
            gripper.apply_preset(key)
            print(f"Applied preset {key}")
