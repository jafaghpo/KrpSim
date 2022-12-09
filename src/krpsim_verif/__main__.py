import sys
import argparse

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="krpsim_verif",
        description="Verify the trace of KrpSim",
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the configuration file",
    )
    parser.add_argument(
        "trace",
        type=str,
        help="Path to the trace file",
    )
    return parser.parse_args(argv)

def main() -> None:
    print(f"krpsim_verif program: {sys.argv[1:]}")

if __name__ == "__main__":
    main()