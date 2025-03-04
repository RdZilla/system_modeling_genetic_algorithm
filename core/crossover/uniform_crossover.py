import numpy as np


def uniform_crossover(self, parent1, parent2):
    """Выполняет однородный кроссовер с заданной вероятностью."""
    prob = self.crossover_kwargs.get("prob")

    mask = np.random.rand(len(parent1)) < prob
    child1 = np.where(mask, parent1, parent2)
    child2 = np.where(mask, parent2, parent1)
    return child1, child2