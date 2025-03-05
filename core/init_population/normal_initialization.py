import numpy as np


def normal_initialization(self):
    """Создает популяцию с нормальным распределением значений.

    Args:
        self

    Returns:
        np.ndarray: Массив популяции размером (pop_size, chrom_length).
    """
    pop_size = self.population_size

    chrom_length = self.initialize_population_kwargs.get("chrom_length")
    mean = self.initialize_population_kwargs.get("mean")
    std = self.initialize_population_kwargs.get("std")

    chrom_length = int(chrom_length) if chrom_length else None
    mean = float(mean) if mean else None
    std = float(std) if std else None

    return np.random.normal(mean, std, size=(pop_size, chrom_length))