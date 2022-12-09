from dataclasses import dataclass, field
import sys
import re

# REGEX: dict[str, str] = {
#     "stock": re.compile(r"^[a-zA-Z]+:[0-9]+$"),
#     "process": re.compile(r"^[a-zA-Z]+:\([a-zA-Z]+:[0-9]+;?\)+:\([a-zA-Z]+:[0-9]+;?\)+:[0-9]+$"),
#     "needs": re.compile(r"(.*?):(.*):+(.*)"),
#     "optimize": re.compile(r"^optimize:\([a-zA-Z]+;?\)+$"),
# }

REGEX = {
    "stock": re.compile(r"^[a-zA-Z]+:[0-9]+$"),
    "process": re.compile(r"^[a-zA-Z]+:\([a-zA-Z]+:[0-9]+;?\)+:\([a-zA-Z]+:[0-9]+;?\)+:[0-9]+$"),
    "needs": re.compile(r"(.*?):(.*):+(.*)"),
    "optimize": re.compile(r"^optimize:\([a-zA-Z]+;?\)+$"),
}

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
        Return the string representation of the stock.
        """
        s = f"\033[1mStock\033[0m -> \033[38;5;155m{self.name}"
        s += f"\033[0m : {self.quantity}"
        return s

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
        s = f"\033[38;5;74m{self.name}\033[0m - \033[1mneeds\033[0m : {self.need} -> "
        s += f"\033[1mresult\033[0m : {self.output} - \033[1mdelay\033[0m : {self.time}"
        return s


@dataclass
class Parser:
    """
    Parser of the configuration file.
    """
    path: str
    stocks: dict[str, Stock] = field(default_factory=dict)
    processes: dict[str, Process] = field(default_factory=dict)
    optimize: list[str] = field(default_factory=list)
    stock_turn: bool = True
    process_turn: bool = False
    optimize_turn: bool = False


    def parse_stock(self, line: str) -> Stock:
        """
        Parse a stock line of the configuration file.
        """
        ocurrences = re.findall(REGEX["stock"], line)
        if not ocurrences:
            sys.exit(f"Error: invalid stock format: {line}")
        name, quantity = ocurrences[0].split(":")
        if not name.isalpha():
            sys.exit(f"Error: invalid stock name: {name}")
        if not quantity.isdigit():
            sys.exit(f"Error: invalid stock quantity: {quantity}")
        return Stock(name, int(quantity))

    def parse_process(self, line: str) -> Process:
        """
        Parse a process line of the configuration file.
        """
        ocurrences = re.findall(REGEX["process"], line)
        if not ocurrences:
            sys.exit(f"Error: invalid process format: {line}")
        name, need, output, time = ocurrences[0].split(":")
        if not name.isalpha():
            sys.exit(f"Error: invalid process name: {name}")
        if not time.isdigit():
            sys.exit(f"Error: invalid process time: {time}")
        need = self.parse_needs(need)
        output = self.parse_needs(output)
        return Process(name, need, output, int(time))

    def parse_optimize(self, line: str) -> list[str]:
        """
        Parse the optimize line of the configuration file.
        """
        ocurrences = re.findall(REGEX["optimize"], line)
        if not ocurrences:
            sys.exit(f"Error: invalid optimize format: {line}")
        return ocurrences[0].split(";")

    def parse_line(self, line: str) -> Process | Stock | list[str]:
        """
        Parse a line of the configuration file and return the corresponding object.
        """
        if REGEX["optimize"].match(line):
            return self.parse_optimize(line)
        elif REGEX["process"].match(line):
            print("process")
            return self.parse_process(line)
        elif REGEX["stock"].match(line):
            return self.parse_stock(line)
        else:
            sys.exit(f"Error: invalid line: {line}")

    def parse_config(self) -> tuple[dict[str, Stock], dict[str, Process], list[str]]:
        """
        Parse the configuration file and return the list of stocks & processes
        as dictionary with their name as key and the stock name(s) to optimize.
        - path: the path to the configuration file

        => Formatting of the configuration file:
        - Stock format: "stock_name:quantity"
        - Processes format: "process_name:needs:outputs:time"
        - Needs/Outputs format: "(stock_name:quantity;stock_name:quantity;...)"
        - Optimize format: "optimize:(stock_name;...)"
        - Comments format: "# ..."
        
        Comments and empty lines are ignored.
        The configuration file will have the following order: stocks, processes, optimize.
        """
        with open(self.path) as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                output = self.parse_line(line)
                if isinstance(output, Stock):
                    if not self.stock_turn:
                        sys.exit(f"Error: invalid line: {line}")
                    print(f"{output}")
                    self.stocks[output.name] = output
                elif isinstance(output, Process):
                    if not self.process_turn:
                        if not self.stock_turn:
                            sys.exit(f"Error: invalid line: {line}")
                        self.stock_turn = False
                        self.process_turn = True
                    print(f"{output}")
                    self.processes[output.name] = output
                elif isinstance(output, list):
                    print(f"\033[1mOptimize\033[0m -> {output}")
                    self.optimize = output
                    break
            return self.stocks, self.processes, self.optimize

