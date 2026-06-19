import argparse

from artis_gripper import ArtisGripper, TeachingPlayer, TeachingSequence


def main():
    parser = argparse.ArgumentParser(description="Replay ARTiS teaching sequence")
    parser.add_argument("sequence")
    parser.add_argument("--config", default="configs/artis_default.yaml")
    parser.add_argument("--speed-scale", type=float, default=1.0)
    args = parser.parse_args()

    sequence = TeachingSequence.load(args.sequence)
    with ArtisGripper(args.config) as g:
        TeachingPlayer(g).replay(sequence, speed_scale=args.speed_scale)


if __name__ == "__main__":
    main()
