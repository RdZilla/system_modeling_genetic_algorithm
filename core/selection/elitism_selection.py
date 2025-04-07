import numpy as np


def elitism_selection(self):
    """Сохраняет лучших индивидов в популяции."""
    _ru_function_name = "Элитарная селекция"
    _ru_elite_size = "Размер элит"

    population = self.population
    fitness = self.fitness

    elite_size = self.selection_kwargs.get("elite_size")

    elite_size = int(elite_size) if elite_size else None

    elite_indices = np.argsort(fitness)[-elite_size:]
    elites = population[elite_indices]
    return elites