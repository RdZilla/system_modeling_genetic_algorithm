import numpy as np


def random_initialization(pop_size, chrom_length):
    """Создает популяцию с равномерным распределением значений.

    Args:
        pop_size (int): Количество индивидов в популяции.
        chrom_length (int): Длина хромосомы.

    Returns:
        np.ndarray: Массив популяции размером (pop_size, chrom_length).
    """
    return np.random.randint(2, size=(pop_size, chrom_length))