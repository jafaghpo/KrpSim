import sys
import argparse

from krpsim.parser import Parser

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="krpsim",
        description="Task scheduling under time/resources constraints",
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the configuration file",
    )
    parser.add_argument(
        "delay",
        type=int,
        help="Time limit for the scheduling",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--cycle",
        type=int,
        default=None,
        help="Maximum umber of cycle for the scheduling",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display more information",
    )
    return parser.parse_args(argv)

def main() -> None:
    print(f"krpsim program: {sys.argv[1:]}")
    args = parse_args(sys.argv[1:])
    parser = Parser(args.file)
    parser.parse_config()

if __name__ == "__main__":
    main()