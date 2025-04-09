def rosenbrock_function(chromosome):
    """Вычисляет значение функции Розенброка."""
    _ru_function_name = "Функция Розенброка"

    return sum(100 * (chromosome[i+1] - chromosome[i]**2)**2 + (1 - chromosome[i])**2
               for i in range(len(chromosome) - 1))