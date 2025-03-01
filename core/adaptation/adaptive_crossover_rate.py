def adaptive_crossover_rate(generation, max_generations, initial_rate=0.7, min_rate=0.5):
    """Динамическое уменьшение вероятности кроссовера по мере развития поколения."""
    rate = initial_rate * (1 - generation / max_generations)
    return max(rate, min_rate)