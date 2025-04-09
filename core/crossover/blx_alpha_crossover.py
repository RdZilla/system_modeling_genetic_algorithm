import numpy as np


def blx_alpha_crossover(self, parent1, parent2):
    """Выполняет BLX-α кроссовер для вещественных значений."""

    _ru_function_name = "BLX-α кроссовер для вещественных значений"
    _ru_alpha = "Альфа"

    alpha = self.crossover_kwargs.get("alpha")
    alpha = float(alpha) if alpha else None

    min_vals = np.minimum(parent1, parent2)
    max_vals = np.maximum(parent1, parent2)
    diff = max_vals - min_vals
    lower_bound = min_vals - alpha * diff
    upper_bound = max_vals + alpha * diff
    child1 = np.random.uniform(lower_bound, upper_bound)
    child2 = np.random.uniform(lower_bound, upper_bound)
    return child1, child2