def adaptive_elitism_size(self):
    """Увеличение размера элитной группы по мере развития поколения."""

    generation = self.generation
    max_generations = self.max_generations
    initial_size = self.adaptation_kwargs.get("initial_size")
    size = self.adaptation_kwargs.get("size")

    initial_size = float(initial_size) if initial_size else None
    size = float(size) if size else None

    size = initial_size + (generation / max_generations) * (size - initial_size)
    return int(size)