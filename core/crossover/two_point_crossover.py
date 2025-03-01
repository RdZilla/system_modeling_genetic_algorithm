import numpy as np


def two_point_crossover(parent1, parent2):
    """Выполняет двухточечный кроссовер между двумя родителями."""
    point1, point2 = sorted(np.random.choice(range(1, len(parent1)), 2, replace=False))
    child1 = np.concatenate((parent1[:point1], parent2[point1:point2], parent1[point2:]))
    child2 = np.concatenate((parent2[:point1], parent1[point1:point2], parent2[point2:]))
    return child1, child2