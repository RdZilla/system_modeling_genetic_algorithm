import numpy as np


def bitwise_mutation(chromosome, mutation_rate=0.01):
    """Выполняет побитовую мутацию с заданной вероятностью.

    Args:
        chromosome (np.ndarray): Бинарная хромосома.
        mutation_rate (float): Вероятность мутации каждого гена.

    Returns:
        np.ndarray: Мутировавшая хромосома.
    """
    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    mutated = np.where(mutation_mask, 1 - chromosome, chromosome)
    return mutated