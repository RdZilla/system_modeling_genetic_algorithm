import numpy as np


def convergence_fitness_termination(self):
    """Завершается, когда изменения в фитнес функции становятся малыми."""
    _ru_function_name = "Стагнация фитнес функции"
    _ru_stagnation_threshold = "Порог застоя"
    _ru_stagnation_generations = "Количество поколений"
    _ru_min_max_rule = "Правило min или max"

    fitness = self.fitness
    previous_fitness = self.previous_fitness

    stagnation_threshold = self.termination_kwargs.get("stagnation_threshold")
    stagnation_generations = self.termination_kwargs.get("stagnation_generations")
    min_max_rule = self.termination_kwargs.get("min_max_rule")

    stagnation_threshold = float(stagnation_threshold) if stagnation_threshold else None
    stagnation_generations = int(stagnation_generations) if stagnation_generations else None

    if not previous_fitness:
        return False

    if min_max_rule == "max":
        diff = np.max(fitness) - np.max(previous_fitness)
    else:
        diff = np.min(fitness) - np.min(previous_fitness)


    if not diff < stagnation_threshold:
        return False

    self.termination_kwargs["stagnation_generation_count"] += 1
    if self.termination_kwargs["stagnation_generation_count"] >= stagnation_generations:
        return True

    return False


