import numpy as np


def convergence_termination(population, prev_population, threshold=1e-6):
    """Завершается, когда изменения в популяции становятся малыми."""
    diff = np.linalg.norm(population - prev_population)
    return diff < threshold