from dataclasses import dataclass
import re
import os

@dataclass
class Stock:
    """
    A stock is a resource that can be used in a process.
    - name: the name of the stock
    - quantity: the quantity of the stock
    """
    name: str
    quantity: int

    def __str__(self) -> str:
        """
        String representation of the stock.

        Returns:
            A string representing the stock.
        """
        s = f"\033[38;5;155m{self.name}\033[0m: {self.quantity}"
        return s
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class Process:
    """
    A process is a task that can be executed.
    - name: the name of the process
    - need: the list of stocks needed to execute the process
    - output: the list of stocks produced by the process
    - time: the time needed to execute the process
    """
    name: str
    need: list[Stock]
    output: list[Stock]
    time: int

    def __str__(self) -> str:
        s = f"\033[38;5;74m{self.name}\033[0m (time: {self.time})\n"
        s += f"\t\033[1mInput\033[0m: {self.need}\n\t\033[1mOutput\033[0m: {self.output}"
        return s

def get_lines(path: str) -> list[str]:
    """
    Reads the file at the specified path, removes leading and trailing whitespaces,
    and returns the lines without comment lines.

    Args:
        path: A string representing the path of the file.
    Returns:
        A list of strings representing the lines of the file without leading
        and trailing whitespaces and without comment lines.
    Raises:
        FileNotFoundError: if the file does not exist or is empty.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' does not exist")
    cleaned_lines = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                cleaned_lines.append(line)
    if not cleaned_lines:
        raise FileNotFoundError(f"File '{path}' is empty")
    return cleaned_lines

def parse_stock(stock: str) -> Stock:
    """
    Parse a stock string and returns a Stock object containing
    the name and the quantity of the stock.

    Args:
        stock: A string representing the stock in the format of "name:quantity"
    Returns:
        A Stock object containing the name and the quantity of the stock.
    Raises:
        ValueError: if the stock string does not match the expected format.
    """
    stock_match = re.match(r"(\w+):(\d+)", stock)
    if stock_match is None:
        raise ValueError(f"Invalid format for stock: '{stock}'")
    return Stock(stock_match.group(1), int(stock_match.group(2)))

def parse_process(process: str) -> Process:
    """
    Parse a process line and returns a Process object.

    Args:
        process: A string representing the process line.
    Returns:
        A Process object containing the name, time, input & output stocks.
    Raises:
        ValueError: if the process line does not match the expected format.
    """
    match = re.match(r"^(\w+):\((.*)\):\((.*)\):(\d+)$", process)
    if match is None:
        raise ValueError(f"Invalid format for process: '{process}'")
    name, needs, outputs, time = match.groups()
    need = []
    for stock in needs.split(";"):
        need.append(parse_stock(stock))
    output = []
    for stock in outputs.split(";"):
        output.append(parse_stock(stock))
    return Process(name, need, output, int(time))

def parse_optimize(stocks: dict[str, int], optimize: str) -> list[str]:
    """
    Parse the optimize line and returns the list of stocks to optimize.

    Args:
        optimize: A string representing the optimize line.
    Returns:
        A list of stocks to optimize.
    Raises:
        ValueError: if the optimize line does not match the expected format.
    """
    match = re.match(r"^optimize:\(([\w;]+)\)$", optimize)
    if match is None:
        raise ValueError(f"Invalid format for optimize: '{optimize}'")
    optimize = [stock for stock in optimize.split(":")[1][1:-1].split(";")]
    for stock in optimize:
        if optimize != "time" and not stock in stocks:
            raise ValueError(f"Stock '{stock}' to optimize is not defined")
    return optimize

def update_stocks_quantity(stocks: dict[str, int], process: Process):
    """
    Updates the list of stocks by adding the stocks needed and returned by the process.

    Args:
        stocks: A dictionary of stocks in the format of "name:quantity"
        process: A Process object containing the name, time, input & output stocks.
    Returns:
        None
    """
    for stock in process.need:
        if not stock.name in stocks:
            stocks[stock.name] = 0
    for stock in process.output:
        if not stock.name in stocks:
            stocks[stock.name] = 0

def parse_lines(file: list[str]) -> tuple[dict[str, int], list[Process], str]:
    """
    Parses each line of the config file to extract the base stocks, processes and
    the stocks to optimize.

    Args:
        file: list of strings representing the lines of the config file
    Returns:
        A tuple containing a dictionary of stocks, a list of processes 
        and a list of stocks to optimize.
        
        Each stock in the dictionary is represented by a key-value pair, where the key
        is the name of the stock and the value is the quantity of the stock.
        
        Each process in the list of processes is represented by a Process object,
        which contains the name, the list of needed stocks,
        the list of output stocks, and the time needed to execute the process.
        
        Each stock to optimize is a string.
    Raises:
        ValueError: if the line does not match the expected format
        (e.g. a process line is found when a stock line was expected)
    """
    stocks, processes, optimize = {}, [], []
    status = "stock"
    for line in file:
        if 'optimize' in line:
            if not processes:
                raise ValueError(f"Cant optimize before having any process")
            if status != "process":
                raise ValueError(f"Expected {status} for line: '{line}'")
            status = "optimize"
            optimize = parse_optimize(stocks, line)
        elif '(' in line:
            if status == "optimize":
                raise ValueError(f"Expected {status} for line: '{line}'")
            status = "process"
            process = parse_process(line)
            processes.append(process)
            update_stocks_quantity(stocks, process)
        else:
            if status != "stock":
                raise ValueError(f"Expected {status} for line: '{line}'")
            status = "stock"
            stock = parse_stock(line)
            stocks[stock.name] = stock.quantity
    if not processes:
        raise ValueError(f"Expected at least one process")
    if status != "optimize":
        raise ValueError(f"No stock to optimize")
    return stocks, processes, optimize