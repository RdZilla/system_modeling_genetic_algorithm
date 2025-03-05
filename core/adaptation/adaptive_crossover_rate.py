def adaptive_crossover_rate(self):
    """Динамическое уменьшение вероятности кроссовера по мере развития поколения."""
    generation = self.generation
    max_generations = self.max_generations
    initial_rate = self.adaptation_kwargs.get("initial_rate")
    min_rate = self.adaptation_kwargs.get("min_rate")

    initial_rate = float(initial_rate) if initial_rate else None
    min_rate = float(min_rate) if min_rate else None

    rate = initial_rate * (1 - generation / max_generations)
    return max(rate, min_rate)