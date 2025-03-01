def generation_limit_termination(generation, max_generations):
    """Завершается, когда достигнут предел количества поколений."""
    return generation >= max_generations