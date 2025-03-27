import numpy as np


def random_initialization(self):
    """Создает популяцию с равномерным распределением значений.

    Args:
       self

    Returns:
        np.ndarray: Массив популяции размером (pop_size, chrom_length).
    """
    pop_size = self.population_size
    chrom_length = self.initialize_population_kwargs.get("chrom_length")

    chrom_length = int(chrom_length) if chrom_length else None

    return np.random.randint(2, size=(pop_size, chrom_length))