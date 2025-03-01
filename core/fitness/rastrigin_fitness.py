import numpy as np


def rastrigin_function(chromosome):
    """Вычисляет значение функции Растригина для заданной хромосомы."""
    A = 10
    return A * len(chromosome) + sum(x**2 - A * np.cos(2 * np.pi * x) for x in chromosome)