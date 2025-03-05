import numpy as np


def creep_mutation(self, chromosome):
    """Выполняет ползучую мутацию для вещественных значений."""
    mutation_rate = self.mutation_rate

    creep_range = self.mutation_kwargs.get("creep_range")

    creep_range = float(creep_range) if creep_range else None

    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    creep_values = np.random.uniform(-creep_range, creep_range, size=len(chromosome))
    mutated = chromosome + mutation_mask * creep_values
    return mutated