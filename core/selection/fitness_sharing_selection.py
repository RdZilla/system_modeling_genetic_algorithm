import numpy as np

from core.selection.roulette_wheel_selection import roulette_wheel_selection


def fitness_sharing_selection(self):
    """Учитывает разнообразие популяции через разделение фитнеса."""
    _ru_function_name = "Разнообразие популяции через разделение фитнеса"
    _ru_sigma_share = "Порог схожести (σ для фитнес-шейринга)"
    _ru_alpha = "Альфа"

    population = self.population
    fitness = self.fitness

    sigma_share = self.selection_kwargs.get("sigma_share")
    alpha = self.selection_kwargs.get("alpha")

    sigma_share = float(sigma_share) if sigma_share else None
    alpha = float(alpha) if alpha else None

    shared_fitness = np.copy(fitness)
    for i in range(len(population)):
        for j in range(len(population)):
            if i != j:
                dist = np.linalg.norm(population[i] - population[j])
                if dist < sigma_share:
                    shared_fitness[i] *= (1 - (dist / sigma_share) ** alpha)
    return roulette_wheel_selection(population, shared_fitness)