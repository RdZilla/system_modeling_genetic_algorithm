import time

import numpy as np
# from multiprocessing import Pool
from billiard.pool import Pool

from core.models.mixin_models.ga_mixin_models import GeneticAlgorithmMixin



class MasterWorkerGA(GeneticAlgorithmMixin):
    REQUIRED_PARAMS = [
        *GeneticAlgorithmMixin.REQUIRED_PARAMS
    ]

    def __init__(self,
                 population_size,
                 max_generations,

                 mutation_rate,
                 crossover_rate,

                 num_workers=None,

                 adaptation_function=None,
                 adaptation_kwargs=None,

                 crossover_function=None,
                 crossover_kwargs=None,

                 fitness_function=None,
                 fitness_kwargs=None,

                 initialize_population_function=None,
                 initialize_population_kwargs=None,

                 mutation_function=None,
                 mutation_kwargs=None,

                 selection_function=None,
                 selection_kwargs=None,

                 termination_function=None,
                 termination_kwargs=None,
                 logger=None):

        super().__init__(population_size,
                         max_generations,
                         mutation_rate,
                         crossover_rate,
                         num_workers,
                         adaptation_function,
                         adaptation_kwargs,
                         crossover_function,
                         crossover_kwargs,
                         fitness_function,
                         fitness_kwargs,
                         initialize_population_function,
                         initialize_population_kwargs,
                         mutation_function,
                         mutation_kwargs,
                         selection_function,
                         selection_kwargs,
                         termination_function,
                         termination_kwargs,
                         logger)

        self.generation = None

        self.population = None
        self.previous_population = None

        self.fitness = None
        self.previous_fitness = None

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы в популяции с использованием Celery."""
        with Pool(processes=self.num_workers) as pool:
            fitness_values = pool.map(self.fitness_function, population)
        return np.array(fitness_values)

    def check_termination_conditions(self):
        """Проверка условий завершения алгоритма."""
        if self.termination_function:
            if self.termination_function(self):
                self.logger.logger_log.info(f"[{self.task_id}] || A termination function stopped the algorithm")
                return True

        if self.generation >= self.max_generations:
            self.logger.logger_log.info(f"[{self.task_id}] || The generational limit has been reached")
            return True

        return False

    def run_generation(self):
        """Запуск одного поколения алгоритма."""
        self.fitness = self.evaluate_fitness(self.population)
        self.log_process(self.task_id, self.generation, self.population, self.fitness)
        if self.check_termination_conditions():
            return True

        self.previous_population = self.population
        self.previous_fitness = self.fitness

        offspring = self.crossover_and_mutate()

        self.population = offspring

        if self.adaptation_function:  # TODO Все функции адаптации требуют доработки
            self.adaptation_function(self)
        return False

    def crossover_and_mutate(self):
        """Проводит кроссовер и мутацию на основе вероятностей событий."""
        offspring = []
        for _ in range(self.population_size // 2):
            parent1 = self.selection_function(self)
            parent2 = self.selection_function(self)
            while np.array_equal(parent1, parent2):
                parent2 = self.selection_function(self)

            if np.random.rand() < self.crossover_rate:
                child1, child2 = self.crossover_function(self, parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if np.random.rand() < self.mutation_rate:
                child1 = self.mutation_function(self, child1)
            if np.random.rand() < self.mutation_rate:
                child2 = self.mutation_function(self, child2)
            offspring.extend([child1, child2])
        return np.array(offspring)

    def start_calc(self):
        self.population = self.initialize_population_function(self)
        if self.termination_kwargs:
            self.termination_kwargs["start_time"] = time.time()

        for generation in range(1, self.max_generations + 1):
            self.generation = generation
            terminate_flag = self.run_generation()
            if terminate_flag:
                break
