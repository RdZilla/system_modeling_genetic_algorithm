def arithmetic_crossover(parent1, parent2, alpha=0.5):
    """Выполняет арифметический кроссовер для вещественных значений."""
    child1 = alpha * parent1 + (1 - alpha) * parent2
    child2 = alpha * parent2 + (1 - alpha) * parent1
    return child1, child2