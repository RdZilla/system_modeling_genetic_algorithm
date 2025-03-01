import numpy as np


def adaptive_mutation(chromosome, mutation_rate, generation, max_generations):
    """Изменяет вероятность мутации в зависимости от поколения."""
    adaptive_rate = mutation_rate * (1 - generation / max_generations)
    mutation_mask = np.random.rand(len(chromosome)) < adaptive_rate
    mutated = np.where(mutation_mask, 1 - chromosome, chromosome)
    return mutated