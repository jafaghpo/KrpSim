from dataclasses import dataclass, field
from typing import Generic, TypeVar
from copy import deepcopy
from math import ceil
import numpy as np

from krpsim.parser import Process

T = TypeVar("T")


@dataclass
class Exec:
    """
    Wrapper around a process and the number of time it needs to be
    executed to produce enough stock for the parent process

    - name: name of the process
    - times: number of times the process is needed to produce enough stock
    """

    name: str
    times: int

    def __str__(self) -> str:
        return f"[{self.name} * {self.times}]"


@dataclass
class Node:
    """
    Collection of processes and stock

    - plist: list of Exec instances
    - stock: stock produced by the processes
    - depth: distance from the starting process
    """

    plist: list[Exec]
    stock: dict[str, int]
    depth: int = 0

    def __str__(self) -> str:
        string: str = f"Depth\033[0m: {self.depth} \033[38;5;74mList\033[0m: "
        for process in self.plist:
            string += f"[{process.name} * {process.times}] "
        return string

    def __add__(self, other):
        return Node([*self.plist, *other.plist], self.depth, self.stock)

    def __radd__(self, other):
        return self if other == 0 else self.__add__(other)

    @staticmethod
    def combinations(matrix: list[list[Generic[T]]]) -> list[list[T]]:
        """
        Get the combinations of elements in the matrix
        returns: matrix of combinations
        example:
        matrix = [[1, 2, 3], [4, 5], [6, 7]]
        Node.combinations(matrix)
        [[1, 4, 6],
        [1, 5, 6],
        [2, 4, 6],
        [2, 5, 6],
        [3, 4, 6],
        [3, 5, 6],
        [1, 4, 7],
        [1, 5, 7],
        [2, 4, 7],
        [2, 5, 7],
        [3, 4, 7],
        [3, 5, 7]])
        """
        return np.array(np.meshgrid(*matrix)).transpose().tolist()


@dataclass
class Graph:
    """
    Class representing a graph of processes connected to each other by the
    stock they produce/need.

    - process: dict of processes.
    - stock: dict of stocks. dict[key: stock name, value: quantity]
    - optimize: name of stock to optimize
    - needs: dict of processes regrouped by the stock they need.
    """

    process: dict[str, Process]
    stock: dict[str, int]
    optimize: str
    needs: dict[str, list[Process]] = field(default_factory=dict)
    outputs: dict[str, list[Process]] = field(default_factory=dict)

    def __str__(self) -> str:
        """
        Return a string representation of the graph
        """
        string: str = f"\033[38;5;74mStocks\033[0m:\n"
        for stock, quantity in self.stock.items():
            string += f"- \033[38;5;62m{stock}\033[0m: {quantity}\n"
        string += f"\n\033[38;5;74mOptimize\033[0m: {self.optimize}\n\n"
        string += f"\033[38;5;74mProcesses\033[0m: \n"
        for process in self.process.values():
            string += f"- {process}\n"
        string += f"\033[38;5;74mOutputs\033[0m: \n"
        for stock, process in self.outputs.items():
            string += f"\033[38;5;62m{stock}\033[0m: "
            for p in process:
                string += f"\033[38;5;70m{p.name}\033[0m: {p.output[stock]}, "
            string += "\n"
        string += f"\n\033[38;5;74mNeeds\033[0m: \n"
        for stock, process in self.needs.items():
            string += f"\033[38;5;62m{stock}\033[0m: "
            for p in process:
                string += f"\033[38;5;70m{p.name}\033[0m: {p.need[stock]}, "
            string += "\n"
        return string

    def sort(self) -> None:
        """
        Method that sorts processes by their needs and products
        """
        for stock, process in self.needs.items():
            process.sort(key=lambda p: p.need[stock])
        for stock, process in self.outputs.items():
            process.sort(key=lambda p: p.output[stock], reverse=True)

    def build(self) -> None:
        """
        Method that builds a graph by regrouping and
        """
        for process in self.process.values():
            for stock in process.need:
                self.needs.setdefault(stock, []).append(process)
                self.stock.setdefault(stock, 0)
            for stock in process.output:
                self.outputs.setdefault(stock, []).append(process)
                self.stock.setdefault(stock, 0)

    def get_root(self) -> Node:
        """
        Get root nodes that outputs the stock to optimize

        returns: a node with a list of process that outputs the stock to optimize
        """
        plist = [Exec(p.name, 1) for p in self.outputs[self.optimize]]
        return Node(plist, deepcopy(self.stock))

    def get_process_children(
        self, parent_process: Exec, depth: int, stock: dict[str, int]
    ) -> list[Node]:
        """
        Get all possible nodes that produce stocks that is needed by parent

        returns: list of combinations of nodes that outputs stocks needed by
            one of the process (parent) of the parent node
        """
        matrices = []
        for need, qty in self.process[parent_process.name].need.items():
            if stock.get(need, 1) >= qty:
                continue
            matrices.append(
                [
                    Exec(p.name, ceil(qty / (p.output[need] + stock[need])))
                    for p in self.outputs[need]
                ]
            )
        print(f"matrices: {matrices}")
        combinations = Node.combinations(matrices)
        return [Node(lst, deepcopy(stock), depth + 1) for lst in combinations]

    def get_children(self, parent: Node) -> list[Node]:
        """
        Get a combination of all possible needed process as nodes

        parent: current node of processes
        returns: list of combinations of nodes that outputs stocks needed by
            all the processes in the parent node
        """
        nodes_lists = [
            self.get_process_children(process, parent.depth, parent.stock)
            for process in parent.plist
        ]
        depth = lambda L: isinstance(L, list) and max(map(depth, L))+1
        print(f"depth: {depth(nodes_lists)}")
        print(f"nodes_lists:")
        for nodes in nodes_lists:
            print(nodes)
        nodes_combinations = Node.combinations(nodes_lists)
        # print(f"nodes_combinations (len = {len(nodes_combinations[0][0])}):")
        # for nodes in nodes_combinations[0][0]:
        #     for node in nodes:
        #         print(node)
        children = [sum(nodes) for nodes in nodes_combinations]
        parent.children = children
        return children

    def get_sequences(self, max_cycle: int = 10000) -> list[list[Node]]:
        """
        Get all paths of processes recursively

        max_cycle: maximum number of cycles that a sequence of process can take
        returns: list of all sequences of process that optimize the wanted stock
        """
        pass
