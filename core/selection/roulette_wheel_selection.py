import numpy as np


def roulette_wheel_selection(population, fitness):
    """Выполняет селекцию методом рулетки."""
    fitness_sum = np.sum(fitness)
    selection_probs = fitness / fitness_sum
    chosen_index = np.random.choice(len(population), p=selection_probs)
    return population[chosen_index]