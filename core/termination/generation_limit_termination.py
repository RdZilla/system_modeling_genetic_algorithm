def generation_limit_termination(self):
    """Завершается, когда достигнут предел количества поколений."""
    generation = self.generation
    max_generations = self.max_generations

    return generation >= max_generations