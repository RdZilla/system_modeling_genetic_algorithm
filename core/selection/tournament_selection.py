import numpy as np


def tournament_selection(population, fitness, tournament_size=3):
    """Выполняет турнирную селекцию.

    Args:
        population (np.ndarray): Массив популяции.
        fitness (np.ndarray): Массив значений фитнес-функции.
        tournament_size (int): Размер турнира.

    Returns:
        np.ndarray: Выбранная хромосома.
    """
    selected = np.random.choice(len(population), tournament_size, replace=False)
    best = selected[np.argmax(fitness[selected])]
    return population[best]