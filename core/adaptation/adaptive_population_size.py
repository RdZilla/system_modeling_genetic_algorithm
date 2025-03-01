def adaptive_population_size(generation, max_generations, initial_size=100, min_size=50):
    """Изменение размера популяции по мере прогресса поколения."""
    size = initial_size - (generation / max_generations) * (initial_size - min_size)
    return int(size)