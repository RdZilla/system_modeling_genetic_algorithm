import numpy as np


def fitness_threshold_termination(self):
    fitness = self.fitness

    fitness_threshold = self.termination_kwargs.get("fitness_threshold")

    fitness_threshold = float(fitness_threshold) if fitness_threshold else None

    """Завершается, когда минимальное значение фитнеса достигает порога."""
    return np.min(fitness) <= fitness_threshold