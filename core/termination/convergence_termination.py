import numpy as np


def convergence_termination(self):
    """Завершается, когда изменения в популяции становятся малыми."""
    population = self.population
    prev_population = self.prev_population

    threshold = self.termination_kwargs.get("threshold")

    threshold = float(threshold) if threshold else None

    diff = np.linalg.norm(population - prev_population)
    return diff < threshold