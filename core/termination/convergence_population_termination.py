import numpy as np


def convergence_population_termination(self):
    """Завершается, когда изменения в популяции становятся малыми."""
    population = self.population
    previous_population = self.previous_population

    stagnation_threshold = self.termination_kwargs.get("stagnation_threshold")
    stagnation_generations = self.termination_kwargs.get("stagnation_generations")

    stagnation_threshold = float(stagnation_threshold) if stagnation_threshold else None
    stagnation_generations = int(stagnation_generations) if stagnation_generations else None


    if not previous_population:
        return False

    diff = np.linalg.norm(population - previous_population)
    if not diff < stagnation_threshold:
        return False

    self.termination_kwargs["stagnation_generation_count"] += 1
    if self.termination_kwargs["stagnation_generation_count"] >= stagnation_generations:
        return True

    return False


