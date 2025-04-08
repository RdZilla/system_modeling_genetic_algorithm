def adaptive_mutation_rate(self):
    """Динамическое уменьшение вероятности мутации по мере развития поколения."""
    _ru_function_name = "Адаптивная вероятность мутации"
    _ru_min_mutation_rate = "Минимальная вероятность мутации"

    generation = self.generation
    max_generations = self.max_generations
    initial_rate = self.mutation_rate
    min_mutation_rate = self.adaptation_kwargs.get("min_mutation_rate")

    initial_rate = float(initial_rate) if initial_rate else None
    min_mutation_rate = float(min_mutation_rate) if min_mutation_rate else None

    calc_rate = initial_rate * (1 - generation / max_generations)
    return max(calc_rate, min_mutation_rate)