def adaptive_elitism_size(generation, max_generations, initial_size=2, max_size=10):
    """Увеличение размера элитной группы по мере развития поколения."""
    size = initial_size + (generation / max_generations) * (max_size - initial_size)
    return int(size)