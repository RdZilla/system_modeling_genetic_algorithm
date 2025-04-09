def adaptive_population_size(self):
    """Изменение размера популяции по мере прогресса поколения."""
    _ru_function_name = "Адаптивный размер популяции"
    _ru_initial_size = ""
    _ru_min_population_size = "Минимальный размер популяции"

    generation = self.generation
    max_generations = self.max_generations
    initial_size = self.adaptation_kwargs.get("initial_size")
    min_population_size = self.adaptation_kwargs.get("min_population_size")

    initial_size = float(initial_size) if initial_size else None
    min_population_size = float(min_population_size) if min_population_size else None

    size = initial_size - (generation / max_generations) * (initial_size - min_population_size)
    return int(size)