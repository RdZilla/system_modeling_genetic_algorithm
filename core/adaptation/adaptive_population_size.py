def adaptive_population_size(self):
    """Изменение размера популяции по мере прогресса поколения."""

    generation = self.generation
    max_generations = self.max_generations
    initial_size = self.adaptation_kwargs.get("initial_size")
    min_size = self.adaptation_kwargs.get("min_size")

    initial_size = float(initial_size) if initial_size else None
    min_size = float(min_size) if min_size else None

    size = initial_size - (generation / max_generations) * (initial_size - min_size)
    return int(size)