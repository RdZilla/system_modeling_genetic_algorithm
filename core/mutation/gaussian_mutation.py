import numpy as np


def gaussian_mutation(chromosome, mutation_rate=0.01, mean=0, std=1):
    """Выполняет гауссовскую мутацию для вещественных значений."""
    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    mutations = np.random.normal(mean, std, size=len(chromosome))
    mutated = chromosome + mutation_mask * mutations
    return mutated