def sphere_function(chromosome):
    """Вычисляет значение сферической функции."""
    return sum(x**2 for x in chromosome)