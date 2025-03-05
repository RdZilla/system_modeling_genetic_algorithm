import numpy as np


def single_point_crossover(self, parent1, parent2):
    """Выполняет одноточечный кроссовер между двумя родителями.

    Args:
        parent1 (np.ndarray): Первая родительская хромосома.
        parent2 (np.ndarray): Вторая родительская хромосома.

    Returns:
        tuple: Две дочерние хромосомы.
    """
    point = np.random.randint(1, len(parent1))
    child1 = np.concatenate((parent1[:point], parent2[point:]))
    child2 = np.concatenate((parent2[:point], parent1[point:]))
    return child1, child2