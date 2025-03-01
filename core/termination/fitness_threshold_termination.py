import numpy as np


def fitness_threshold_termination(fitness, fitness_threshold):
    """Завершается, когда минимальное значение фитнеса достигает порога."""
    return np.min(fitness) <= fitness_threshold