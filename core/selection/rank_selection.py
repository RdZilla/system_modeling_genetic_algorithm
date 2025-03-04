import numpy as np


def rank_selection(self):
    """Выполняет ранговую селекцию."""

    population = self.population
    fitness = self.fitness

    ranks = np.argsort(np.argsort(fitness))
    selection_probs = ranks / np.sum(ranks)
    chosen_index = np.random.choice(len(population), p=selection_probs)
    return population[chosen_index]