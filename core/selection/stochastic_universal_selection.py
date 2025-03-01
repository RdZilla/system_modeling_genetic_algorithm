import numpy as np


def stochastic_universal_selection(population, fitness, num_selected):
    """Выполняет стохастическую универсальную селекцию."""
    fitness_sum = np.sum(fitness)
    selection_probs = fitness / fitness_sum
    start = np.random.uniform(0, 1 / num_selected)
    pointers = start + np.arange(num_selected) / num_selected
    cumulative_probs = np.cumsum(selection_probs)
    selected = []
    for pointer in pointers:
        selected_idx = np.where(cumulative_probs >= pointer)[0][0]
        selected.append(population[selected_idx])
    return np.array(selected)