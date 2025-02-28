from billiard.pool import Pool
import random

from core.models.GA_base_model import GeneticAlgorithm


class MasterWorkerGA(GeneticAlgorithm):
    required_params = [
        "algorithm",
        "generations",
        "population_size",
        "mutation_rate",
        "crossover_rate",
        "fitness_function",
    ]

    def __init__(self, population_size, mutation_rate, crossover_rate,
                 population=None, fitness_function=None, logger=None):
        self.population = population
        super().__init__(population_size, mutation_rate, crossover_rate, fitness_function, logger)

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
        with Pool(processes=4) as pool:
            fitness_values = pool.map(self.evaluate_fitness_worker, self.population)
        return fitness_values

    def run(self, task_id, generations, task_config):
        self.logger.logger_log.info(f"[Task id: {task_id}] || started with config: {task_config}")

        """Запуск алгоритма"""
        for gen in range(generations):  # TODO: add try-except block to set status ERROR
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

            self.logger.log(task_id, gen, best_fitness, avg_fitness)

        self.finish(task_id)
        self.logger.logger_log.info("Algorithm finished successfully")
