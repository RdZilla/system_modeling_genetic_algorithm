import numpy as np


def fitness_threshold_termination(self):
    """Завершается, когда значение фитнеса достигает порога."""
    _ru_function_name = "Порог фитнес функции"
    _ru_fitness_threshold = "Порог фитнес функции"
    _ru_min_max_rule = "Правило min или max"

    fitness = self.fitness

    fitness_threshold = self.termination_kwargs.get("fitness_threshold")
    min_max_rule = self.termination_kwargs.get("min_max_rule")

    fitness_threshold = float(fitness_threshold) if fitness_threshold else None

    if min_max_rule == "max":
        return np.max(fitness) >= fitness_threshold
    else:
        return np.min(fitness) <= fitness_threshold

