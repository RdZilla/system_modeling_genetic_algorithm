import numpy as np

from core.selection.roulette_wheel_selection import roulette_wheel_selection


def fitness_sharing_selection(self):
    """Учитывает разнообразие популяции через разделение фитнеса."""
    population = self.population
    fitness = self.fitness

    sigma_share = self.fitness_kwargs.get("sigma_share")
    alpha = self.fitness_kwargs.get("alpha")

    shared_fitness = np.copy(fitness)
    for i in range(len(population)):
        for j in range(len(population)):
            if i != j:
                dist = np.linalg.norm(population[i] - population[j])
                if dist < sigma_share:
                    shared_fitness[i] *= (1 - (dist / sigma_share) ** alpha)
    return roulette_wheel_selection(population, shared_fitness)