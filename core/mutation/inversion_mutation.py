import numpy as np


def inversion_mutation(self, chromosome):
    """Переворачивает случайный подотрезок хромосомы."""
    start, end = sorted(np.random.choice(len(chromosome), 2, replace=False))
    chromosome[start:end] = chromosome[start:end][::-1]
    return chromosome