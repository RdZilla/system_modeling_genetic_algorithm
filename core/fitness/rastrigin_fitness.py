import numpy as np

def rastrigin(individual):
    """Функция Растригина"""
    A = 10
    return A + individual**2 - A * np.cos(2 * np.pi * individual)
