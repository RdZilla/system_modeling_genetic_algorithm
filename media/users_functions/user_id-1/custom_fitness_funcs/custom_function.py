import numpy as np

def custom_function(individual):
    """Пользовательская фитнес-функция (пример: модифицированная функция Растригина)"""
    A = 10
    return A + individual**2 - A * np.cos(2 * np.pi * individual) + 5 * np.sin(2 * np.pi * individual)
