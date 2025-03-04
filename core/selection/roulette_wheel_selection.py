import numpy as np


def roulette_wheel_selection(self):
    """Выполняет селекцию методом рулетки."""
    population = self.population
    fitness = self.fitness

    fitness_sum = np.sum(fitness)
    selection_probs = fitness / fitness_sum
    chosen_index = np.random.choice(len(population), p=selection_probs)
    return population[chosen_index]