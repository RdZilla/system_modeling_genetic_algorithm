def adaptive_mutation_rate(self):
    """Динамическое уменьшение вероятности мутации по мере развития поколения."""

    generation = self.generation
    max_generations = self.max_generations
    initial_rate = self.adaptation_kwargs.get("initial_rate")
    rate = self.adaptation_kwargs.get("rate")

    initial_rate = float(initial_rate) if initial_rate else None
    rate = float(rate) if rate else None

    calc_rate = initial_rate * (1 - generation / max_generations)
    return max(calc_rate, rate)