import numpy as np

from core.init_population.random_initialization import random_initialization


def custom_initialization(known_solutions, pop_size, chrom_length):
    """Создает популяцию, включающую заранее известные хорошие решения.

    Args:
        known_solutions (list): Список известных хороших решений.
        pop_size (int): Количество индивидов в популяции.
        chrom_length (int): Длина хромосомы.

    Returns:
        np.ndarray: Массив популяции.
    """
    pop = np.zeros((pop_size, chrom_length))
    num_known = min(len(known_solutions), pop_size)
    pop[:num_known] = known_solutions[:num_known]
    if num_known < pop_size:
        pop[num_known:] = random_initialization(pop_size - num_known, chrom_length)
    return pop