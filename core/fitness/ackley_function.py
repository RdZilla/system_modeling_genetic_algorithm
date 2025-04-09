import numpy as np


def ackley_function(chromosome):
    """Вычисляет значение функции Акермана для заданной хромосомы."""
    _ru_function_name = "Функция Акермана"

    a = 20
    b = 0.2
    c = 2 * np.pi
    d = len(chromosome)
    sum1 = sum(x**2 for x in chromosome) / d
    sum2 = sum(np.cos(c * x) for x in chromosome) / d
    return -a * np.exp(-b * np.sqrt(sum1)) - np.exp(sum2) + a + np.exp(1)