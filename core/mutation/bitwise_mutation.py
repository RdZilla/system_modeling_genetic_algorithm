import numpy as np


def bitwise_mutation(self, chromosome):
    """Выполняет побитовую мутацию с заданной вероятностью.

    Args:
        self: Ссылка на класс
        chromosome (np.ndarray): Бинарная хромосома.

    Returns:
        np.ndarray: Мутировавшая хромосома.
    """
    _ru_function_name = "Побитовая мутация"

    mutation_rate = self.mutation_rate

    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    mutated = np.where(mutation_mask, 1 - chromosome, chromosome)
    return mutated