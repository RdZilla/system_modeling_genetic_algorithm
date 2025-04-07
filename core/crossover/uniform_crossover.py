import numpy as np


def uniform_crossover(self, parent1, parent2):
    """Выполняет однородный кроссовер с заданной вероятностью."""
    _ru_function_name = "Однородный кроссовер с заданной вероятностью"
    _ru_prob = "Вероятность"

    prob = self.crossover_kwargs.get("prob")
    prob = float(prob) if prob else None

    mask = np.random.rand(len(parent1)) < prob
    child1 = np.where(mask, parent1, parent2)
    child2 = np.where(mask, parent2, parent1)
    return child1, child2