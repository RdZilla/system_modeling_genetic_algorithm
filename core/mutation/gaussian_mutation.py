import numpy as np


def gaussian_mutation(self, chromosome):
    """Выполняет гауссовскую мутацию для вещественных значений."""
    mutation_rate = self.mutation_rate

    _ru_function_name = "Гауссовская мутация"
    _ru_mean = "Среднее значение"
    _ru_std = "Стандартное отклонение"

    mean = self.mutation_kwargs.get("mean")
    std = self.mutation_kwargs.get("std")

    mean = float(mean) if mean else None
    std = float(std) if std else None

    mutation_mask = np.random.rand(len(chromosome)) < mutation_rate
    mutations = np.random.normal(mean, std, size=len(chromosome))
    mutated = chromosome + mutation_mask * mutations
    return mutated