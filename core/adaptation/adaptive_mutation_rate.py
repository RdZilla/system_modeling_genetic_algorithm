def adaptive_mutation_rate(generation, max_generations, initial_rate=0.01, min_rate=0.001):
    """Динамическое уменьшение вероятности мутации по мере развития поколения."""
    rate = initial_rate * (1 - generation / max_generations)
    return max(rate, min_rate)