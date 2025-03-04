import numpy as np


def elitism_selection(self):
    """Сохраняет лучших индивидов в популяции."""
    population = self.population
    fitness = self.fitness
    elite_size = self.fitness_kwargs.get("elite_size")

    elite_indices = np.argsort(fitness)[-elite_size:]
    elites = population[elite_indices]
    return elites