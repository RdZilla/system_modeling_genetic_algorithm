def arithmetic_crossover(self, parent1, parent2):
    """Выполняет арифметический кроссовер для вещественных значений."""

    alpha = self.crossover_kwargs.get("alpha")
    alpha = float(alpha) if alpha else None

    child1 = alpha * parent1 + (1 - alpha) * parent2
    child2 = alpha * parent2 + (1 - alpha) * parent1
    return child1, child2