import numpy as np


def adaptive_mutation(self, chromosome):
    """Изменяет вероятность мутации в зависимости от поколения."""
    mutation_rate = self.mutation_rate
    generation = self.generation
    max_generations = self.max_generations

    adaptive_rate = mutation_rate * (1 - generation / max_generations)
    mutation_mask = np.random.rand(len(chromosome)) < adaptive_rate
    mutated = np.where(mutation_mask, 1 - chromosome, chromosome)
    return mutated