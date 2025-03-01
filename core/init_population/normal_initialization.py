import numpy as np


def normal_initialization(pop_size, chrom_length, mean=0, std=1):
    """Создает популяцию с нормальным распределением значений.

    Args:
        pop_size (int): Количество индивидов в популяции.
        chrom_length (int): Длина хромосомы.
        mean (float): Среднее значение.
        std (float): Стандартное отклонение.

    Returns:
        np.ndarray: Массив популяции размером (pop_size, chrom_length).
    """
    return np.random.normal(mean, std, size=(pop_size, chrom_length))