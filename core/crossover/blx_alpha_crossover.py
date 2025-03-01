import numpy as np


def blx_alpha_crossover(parent1, parent2, alpha=0.5):
    """Выполняет BLX-α кроссовер для вещественных значений."""
    min_vals = np.minimum(parent1, parent2)
    max_vals = np.maximum(parent1, parent2)
    diff = max_vals - min_vals
    lower_bound = min_vals - alpha * diff
    upper_bound = max_vals + alpha * diff
    child1 = np.random.uniform(lower_bound, upper_bound)
    child2 = np.random.uniform(lower_bound, upper_bound)
    return child1, child2