def sphere_function(chromosome):
    """Вычисляет значение сферической функции."""
    _ru_function_name = "Сферическая функция"

    return sum(x**2 for x in chromosome)