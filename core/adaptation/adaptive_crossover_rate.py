def adaptive_crossover_rate(self):
    """Динамическое уменьшение вероятности кроссовера по мере развития поколения."""
    _ru_function_name = "Адаптивная вероятность кроссинговера"
    _ru_min_crossover_rate = "Минимальная вероятность кроссинговера"

    generation = self.generation
    max_generations = self.max_generations
    initial_rate = self.crossover_rate
    min_crossover_rate = self.adaptation_kwargs.get("min_crossover_rate")

    initial_rate = float(initial_rate) if initial_rate else None
    min_crossover_rate = float(min_crossover_rate) if min_crossover_rate else None

    rate = initial_rate * (1 - generation / max_generations)
    return max(rate, min_crossover_rate)