import random
from typing import Callable
from dataclasses import dataclass
from krpsim.parser import Process, Stock


@dataclass
class Schedule:
    """
    A schedule is a list of processes to execute.
    - processes: the list of processes to execute
    - fitness: the fitness of the schedule
    """

    processes: list[Process]
    stocks: dict[str, int]
    optimize: list[str]
    delay: int

    def fitness(self) -> float:
        """
        Calculate the fitness of the schedule.
        The fitness is a measure of how well the schedule meets the optimize
        and delay constraints.
        """
        # Initialize the fitness value to 0
        fitness = 0.0

        # Calculate the fitness based on the optimize constraint
        for stock in self.optimize:
            if stock in self.stocks:
                fitness += self.stocks[stock]

        # Calculate the fitness based on the delay constraint
        total_time = 0
        for process in self.processes:
            total_time += process.time

        if total_time <= self.delay:
            fitness += 1

        return fitness

    def crossover(self, other):
        """
        Combines this schedule with another schedule to create a new schedule.
        """
        # Select a random point to crossover the two schedules
        crossover_point = random.randint(1, len(self.processes) - 1)

        # Create a new schedule using the processes from this schedule up to the crossover point,
        # and the processes from the other schedule after the crossover point
        new_processes = (
            self.processes[:crossover_point] + other.processes[crossover_point:]
        )

        # Create a new schedule using the stocks, optimize and delay from this schedule
        new_schedule = Schedule(new_processes, self.stocks, self.optimize, self.delay)

        return new_schedule

    def mutate(self):
        """
        Mutates this schedule by randomly swapping two processes.
        """
        # Select two random processes to swap
        i = random.randint(0, len(self.processes) - 1)
        j = random.randint(0, len(self.processes) - 1)

        # Swap the two processes
        self.processes[i], self.processes[j] = self.processes[j], self.processes[i]


def initialize_population(
    num_schedules: int,
    processes: list[Process],
    stocks: dict,
    optimize: list[str],
    delay: int,
) -> list[Schedule]:
    """
    Initialize a population of Schedule objects by randomly generating
    a set number of schedules.

    Args:
        num_schedules: The number of schedules to generate.
        processes: A list of Process objects
        stocks: A dictionary of stocks in the format of "name:quantity"
        optimize: A list of stocks to optimize.
        delay: Time limit for the scheduling

    Returns:
        A list of Schedule objects representing the initialized population.
    """
    population = []
    for i in range(num_schedules):
        # randomly select a subset of processes to include in the schedule
        schedule_processes = random.sample(
            processes, k=random.randint(1, len(processes))
        )
        # create a new Schedule object and add it to the population
        population.append(Schedule(schedule_processes, stocks.copy(), optimize, delay))
    return population


def selection(population: list[Schedule], num_parents: int) -> list[Schedule]:
    """
    Select the best schedules from the population using
    the roulette wheel selection method.

    Args:
        population: A list of Schedule objects representing the population
        num_parents: The number of parents to select from the population
    Returns:
        A list of Schedule objects representing the selected parents
    """
    total_fitness = sum(schedule.fitness for schedule in population)
    parents = []
    for _ in range(num_parents):
        pick = random.uniform(0, total_fitness)
        current = 0
        for schedule in population:
            current += schedule.fitness
            if current > pick:
                parents.append(schedule)
                break
    return parents


def reproduce(population: list[Schedule], num_offspring: int) -> list[Schedule]:
    """
    Creates new schedules by combining the best schedules from the population.

    Args:
        population: A list of Schedule objects representing the current population.
        num_offspring: The number of offspring schedules to be created.

    Returns:
        A list of Schedule objects representing the new offspring schedules.
    """
    offspring = []
    for _ in range(num_offspring):
        parent1 = random.choice(population)
        parent2 = random.choice(population)
        child = parent1.crossover(parent2)
        child.mutate()
        offspring.append(child)
    return offspring


def genetic_algorithm(
    processes: list[Process], stocks: dict, optimize: list[str], delay: int
) -> Schedule:
    num_schedules = 10
    num_generations = 10
    num_offspring = 10
    population = initialize_population(
        num_schedules, processes, stocks, optimize, delay
    )
    for generation in range(num_generations):
        population = reproduce(population, num_offspring)
        population = selection(population)
    return max(population, key=lambda schedule: schedule.fitness())
    # rest of the genetic algorithm logic here
