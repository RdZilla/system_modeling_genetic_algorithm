def arithmetic_crossover(self, parent1, parent2):
    """Выполняет арифметический кроссовер для вещественных значений."""

    _ru_function_name = "Арифметический кроссовер для вещественных значений"
    _ru_alpha = "Альфа"

    alpha = self.crossover_kwargs.get("alpha")
    alpha = float(alpha) if alpha else None

    child1 = alpha * parent1 + (1 - alpha) * parent2
    child2 = alpha * parent2 + (1 - alpha) * parent1
    return child1, child2