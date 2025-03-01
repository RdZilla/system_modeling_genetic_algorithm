import numpy as np


def uniform_crossover(parent1, parent2, prob=0.5):
    """Выполняет однородный кроссовер с заданной вероятностью."""
    mask = np.random.rand(len(parent1)) < prob
    child1 = np.where(mask, parent1, parent2)
    child2 = np.where(mask, parent2, parent1)
    return child1, child2