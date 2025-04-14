from datetime import datetime

import numpy as np
from celery import group, shared_task

from core.models.mixin_models.ga_mixin_models import GeneticAlgorithmMixin


@shared_task
def wrapper_fitness_function(fitness_function, individual):
    fitness_value = fitness_function(individual)
    return fitness_value

class MasterWorkerGA(GeneticAlgorithmMixin):
    REQUIRED_PARAMS = [
        *GeneticAlgorithmMixin.REQUIRED_PARAMS
    ]

    def __init__(self, additional_params, ga_params, functions_routes):

        super().__init__(additional_params, ga_params, functions_routes)

        self.generation = None

        self.population = None
        self.previous_population = None

        self.fitness = None
        self.previous_fitness = None
        self.terminate = False

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы в популяции с использованием Celery."""

        task_group = group(wrapper_fitness_function.s(self.fitness_function, individual) for individual in population)
        results = task_group.apply().get(timeout=300, disable_sync_subtasks=False)
        return np.array(results)

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
            self.terminate = True
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
            self.termination_kwargs["start_time"] = datetime.now()

        for generation in range(1, self.max_generations + 1):
            self.generation = generation
            process = self.logger.get_process_id()
            terminate_flag = self.run_generation()
            self.logger.merge_logs(process + 1)
            if terminate_flag:
                break

        self.logger.create_result_log()
