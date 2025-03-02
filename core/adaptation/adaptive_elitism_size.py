def adaptive_elitism_size(generation, max_generations, initial_size=2, size=10):
    """Увеличение размера элитной группы по мере развития поколения."""
    size = initial_size + (generation / max_generations) * (size - initial_size)
    return int(size)