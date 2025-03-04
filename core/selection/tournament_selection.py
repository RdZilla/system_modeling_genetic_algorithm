import numpy as np


def tournament_selection(self):
    """Выполняет турнирную селекцию.

    Args:
        self

    Returns:
        np.ndarray: Выбранная хромосома.
    """

    population = self.population
    fitness = self.fitness
    tournament_size = self.fitness_kwargs.get("tournament_size")

    selected = np.random.choice(len(population), tournament_size, replace=False)
    best = selected[np.argmax(fitness[selected])]
    return population[best]