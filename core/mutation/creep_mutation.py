import numpy as np


def creep_mutation(chromosome, mutation_rate=0.01, creep_range=0.1):
    """Выполняет ползучую мутацию для вещественных значений."""
    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    creep_values = np.random.uniform(-creep_range, creep_range, size=len(chromosome))
    mutated = chromosome + mutation_mask * creep_values
    return mutated