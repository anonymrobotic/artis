from pathlib import Path
from time import sleep

from artis_gripper import ArtisGripper

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "artis_default.yaml"

with ArtisGripper(CONFIG) as g:
    g.apply_preset("z")     # center base
    sleep(1.0)
    g.jam_off()
    g.apply_preset("x")     # close all four-bar fingers
    sleep(2.0)
    g.jam_on()              # stiffen/fix the palm
    sleep(1.0)
    g.apply_preset("a")     # open fingers away from palm workspace
    sleep(2.0)
    g.jam_off()
