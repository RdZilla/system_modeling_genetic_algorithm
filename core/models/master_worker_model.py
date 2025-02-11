import multiprocessing
import random

from core.models.GA_base_model import GeneticAlgorithm


class MasterWorkerGA(GeneticAlgorithm):
    def initialize_population(self):
        """Генерация случайной популяции"""
        return [random.uniform(-5.12, 5.12) for _ in range(self.population_size)]  # Пример для одномерной задачи

    def selection(self):
        """Простая турнирная селекция"""
        tournament_size = 3
        return max(random.sample(self.population, tournament_size), key=self.fitness_function)

    def crossover(self, parent1, parent2):
        """Одноточечное скрещивание"""
        alpha = random.uniform(0, 1)
        return alpha * parent1 + (1 - alpha) * parent2

    def mutation(self, individual):
        """Гауссовская мутация"""
        return individual + random.gauss(0, self.mutation_rate)

    def evaluate_fitness_worker(self, individual):
        """Функция для вычисления приспособленности в процессе"""
        return self.fitness_function(individual)

    def evaluate_fitness(self):
        """Распределенное вычисление приспособленности"""
        with multiprocessing.Pool() as pool:
            fitness_values = pool.map(self.evaluate_fitness_worker, self.population)
        return fitness_values

    def run(self, generations):
        """Запуск алгоритма"""
        for gen in range(generations):
            fitness_values = self.evaluate_fitness()
            new_population = []
            for _ in range(self.population_size // 2):  # TODO <---- range(self.population_size // 2)     ???????
                # TODO: вынести в отдельную функцию логику деления популяции для отбора.
                #  Дать возможность выбора кастомного конфига деления популяции для выборки

                parent1, parent2 = self.selection(), self.selection()
                child1, child2 = self.crossover(parent1, parent2), self.crossover(parent2, parent1)
                child1, child2 = self.mutation(child1), self.mutation(child2)
                new_population.extend([child1, child2])
            self.population = new_population

            best_fitness = max(fitness_values)
            avg_fitness = sum(fitness_values) / len(fitness_values)

            self.logger.log(gen, best_fitness, avg_fitness)
        self.logger.logger_log.info("Algorithm finished successfully")
