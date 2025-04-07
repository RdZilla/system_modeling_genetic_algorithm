import numpy as np

from core.init_population.random_init import random_init


def custom_initialization(self):
    """Создает популяцию, включающую заранее известные хорошие решения.

    Args:
        self

    Returns:
        np.ndarray: Массив популяции.
    """
    _ru_function_name = "Популяция с заранее известными хорошими решениями"
    _ru_chrom_length = "Длина хромосомы"
    _ru_known_solutions = "Известные решения"

    pop_size = self.population_size

    chrom_length = self.initialize_population_kwargs.get("chrom_length")
    known_solutions = self.initialize_population_kwargs.get("known_solutions")

    chrom_length = int(chrom_length) if chrom_length else None
    if known_solutions:
        known_solutions = known_solutions.split(" ")  # TODO доделать

    pop = np.zeros((pop_size, chrom_length))
    num_known = min(len(known_solutions), pop_size)
    pop[:num_known] = known_solutions[:num_known]
    if num_known < pop_size:
        pop[num_known:] = random_init(pop_size - num_known, chrom_length)
    return pop