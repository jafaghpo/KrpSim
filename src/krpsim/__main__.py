import sys
import argparse

from krpsim.parser import Process, get_lines, parse_lines

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

def display_config(stocks: dict[str, int], processes: list[Process], optimize: list[str]):
    """
    Display the data extracted from the config file.

    Args:
        stocks: A dictionary of stocks in the format of "name:quantity"
        processes: A list of Process objects containing the name, time, input & output of the process.
        optimize: A list of stocks to optimize.
    Returns:
        None
    """
    print(f"[Configuration file parsed]")
    print(f"Stocks:")
    for stock, qty in stocks.items():
        print(f" - {stock: <10}: {qty}")
    print(f"Processes:")
    for process in processes:
        print(f" - {process}")
    print(f"Optimize:")
    for stock in optimize:
        print(f" - {stock}")

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
    if args.verbose:
        display_config(stocks, processes, optimize)

if __name__ == "__main__":
    main()