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

    tournament_size = self.selection_kwargs.get("tournament_size")
    min_max_rule = self.selection_kwargs.get("min_max_rule")

    tournament_size = int(tournament_size) if tournament_size else None

    selected = np.random.choice(len(population), tournament_size, replace=False)
    if  min_max_rule == "min":
        index = selected[np.argmin(fitness[selected])]
    else:
        index = selected[np.argmax(fitness[selected])]
    return population[index]