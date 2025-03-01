import numpy as np


def elitism_selection(population, fitness, elite_size=2):
    """Сохраняет лучших индивидов в популяции."""
    elite_indices = np.argsort(fitness)[-elite_size:]
    elites = population[elite_indices]
    return elites