import numpy as np


def target_solution_termination(self):
    """Завершается, когда найдено решение, соответствующее целевой функции."""
    fitness = self.fitness
    target_fitness = self.termination_kwargs.get("target_fitness")

    return np.min(fitness) <= target_fitness