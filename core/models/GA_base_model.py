from abc import ABC, abstractmethod


class GeneticAlgorithm(ABC):
    def __init__(self, population_size, mutation_rate, crossover_rate, fitness_function, logger):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.fitness_function = fitness_function
        self.population = self.initialize_population()

        self.logger = logger

    @abstractmethod
    def initialize_population(self):
        """Инициализация начальной популяции"""
        pass

    @abstractmethod
    def selection(self):
        """Выбор родителей"""
        pass

    @abstractmethod
    def crossover(self, parent1, parent2):
        """Скрещивание"""
        pass

    @abstractmethod
    def mutation(self, individual):
        """Мутация"""
        pass

    @abstractmethod
    def evaluate_fitness(self):
        """Оценка приспособленности"""
        pass

    @abstractmethod
    def run(self, generations):
        """Запуск алгоритма"""
        pass
