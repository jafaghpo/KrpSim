import sys
import argparse

from krpsim.parser import get_lines, parse_lines
from krpsim.graph import Graph


def parse_args(argv: list[str]) -> argparse.Namespace:
    """
    Parse the command line arguments and returns a Namespace object containing
    the parsed arguments.

    Args:
        argv: A list of strings representing the command line arguments.
    Returns:
        A Namespace object containing the parsed arguments.
    """
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
        nargs="?",
        type=int,
        help="Time limit for the scheduling",
        default=int(1e6),
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


def main():
    """
    Entry point of the program, parse the command line arguments,
    parse the configuration file, and display data if verbose flag is set.

    Returns:
        None
    Raises:
        FileNotFoundError: if the specified file does not exist.
        ValueError: if there is an error parsing the configuration file.
    """
    args = parse_args(sys.argv[1:])
    try:
        lines = get_lines(args.file)
        stocks, processes, optimize = parse_lines(lines)
    except (FileNotFoundError, ValueError) as error:
        sys.exit(f"Error: {error}")
    graph = Graph(processes, stocks, optimize)
    graph.build()
    graph.sort()
    if args.verbose:
        print(graph)
    root = graph.get_root()
    if args.verbose:
        print(root)
    children = graph.get_children(root)
    # if args.verbose:
    #     for node in children:
    #         print(node)

if __name__ == "__main__":
    main()
