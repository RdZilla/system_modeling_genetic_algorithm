import numpy as np


def gaussian_mutation(self, chromosome):
    """Выполняет гауссовскую мутацию для вещественных значений."""
    mutation_rate = self.mutation_rate
    mean = self.mutation_kwargs.get("mean")
    std = self.mutation_kwargs.get("std")

    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    mutations = np.random.normal(mean, std, size=len(chromosome))
    mutated = chromosome + mutation_mask * mutations
    return mutated