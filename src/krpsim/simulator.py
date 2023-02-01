from dataclasses import dataclass

from krpsim.parser import Process, Stock
from krpsim.genetic_algo import Schedule


@dataclass
class Simulator:
    """
    A simulator is used to simulate a schedule and calculate its fitness.
    - stocks: the initial stocks
    - optimize: the list of stocks to optimize
    - delay: the delay constraint
    """

    stocks: dict[str, int]
    optimize: list[str]
    delay: int

    def simulate(self, schedule: Schedule) -> float:
        stocks = (
            self.stocks.copy()
        )  # Create a copy of the initial stocks to avoid modifying the original
        time = 0
        fitness = 0
        for process in schedule.processes:
            # Check if the process can be executed (all needed stocks are available)
            if all(stocks.get(need.name, 0) >= need.quantity for need in process.need):
                # Update the stocks by consuming the needed stocks and producing the output stocks
                for need in process.need:
                    stocks[need.name] -= need.quantity
                for output in process.output:
                    stocks[output.name] += output.quantity
                time += process.time
                # Check if the delay is respected
                if time > self.delay:
                    break
                # If the process produces an optimized stock, increase the fitness value
                for output in process.output:
                    if output.name in self.optimize:
                        fitness += output.quantity
        return fitness
