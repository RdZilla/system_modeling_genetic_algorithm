import numpy as np


def target_solution_termination(fitness, target_fitness):
    """Завершается, когда найдено решение, соответствующее целевой функции."""
    return np.min(fitness) <= target_fitness