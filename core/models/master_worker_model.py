import time
from multiprocessing import cpu_count

import numpy as np
# from multiprocessing import Pool
from billiard.pool import Pool

from core.init_population.random_initialization import random_initialization
from core.selection.tournament_selection import tournament_selection
from modeling_system_backend.settings import DEBUG
from task_modeling.models import Task, Experiment
from task_modeling.utils.set_experiment_status import set_experiment_status


class MasterWorkerGA:
    REQUIRED_PARAMS = [
        "algorithm",
        "population_size",
        "max_generations",

        "mutation_rate",
        "crossover_rate",
        "selection_rate",

        "num_workers",

        "crossover_function",
        "fitness_function",
        "initialize_population_function",
        "mutation_function",
        "selection_function",
    ]

    def __init__(self,
                 population_size,
                 max_generations,

                 mutation_rate,
                 crossover_rate,
                 selection_rate,

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
        """
        population_size: Размер популяции
        max_generations: Максимальное количество поколений

        mutation_rate: Вероятность мутации
        crossover_rate: Вероятность кроссовера
        selection_rate: Вероятность селекции

        num_workers: Количество рабочих процессов для параллельных вычислений

        adaptation_function: Функция адаптации параметров
        crossover_function: Функция кроссовера
        fitness_function: Функция фитнеса
        initialize_population_function: Функция для инициализации популяции
        mutation_function: Функция мутации
        selection_function: Функция селекции
        termination_function: Функция завершения алгоритма

        fitness_threshold: Пороговое значение для фитнеса, при котором алгоритм завершится
        stagnation_threshold: Порог для изменения фитнеса
        stagnation_generations: Количество поколений без улучшений для прекращения работы
        logger: Объект ExperimentLogger для логирования процесса
        """
        # Параметры генетического алгоритма
        self.population_size = population_size
        self.max_generations = max_generations

        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.selection_rate = selection_rate

        self.num_workers = num_workers or cpu_count()

        # Пользовательские функции
        self.adaptation_function = adaptation_function
        self.adaptation_kwargs = adaptation_kwargs

        self.crossover_function = crossover_function
        self.crossover_kwargs = crossover_kwargs

        self.fitness_function = fitness_function
        self.fitness_kwargs = fitness_kwargs

        self.initialize_population_function = initialize_population_function or random_initialization
        self.initialize_population_kwargs = initialize_population_kwargs

        self.mutation_function = mutation_function
        self.mutation_kwargs = mutation_kwargs

        self.selection_function = selection_function or tournament_selection
        self.selection_kwargs = selection_kwargs

        self.termination_function = termination_function
        self.termination_kwargs = termination_kwargs

        self.logger = logger

        self.generation = None
        self.population = None
        self.prev_population = None
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
                self.logger.logger_log.info("Пользовательская функция завершения остановила алгоритм")
                return True
        # fitness_threshold = self.termination_kwargs.get("fitness_threshold", None)
        # if fitness_threshold and np.max(self.fitness) >= fitness_threshold:
        #     print(f"Порог фитнеса достигнут: {np.max(self.fitness)}")
        #     return True
        #
        # stagnation_threshold = self.termination_kwargs.get("stagnation_threshold", None)
        # stagnation_generations = self.termination_kwargs.get("stagnation_generations")
        # if stagnation_threshold and stagnation_generations and self.generation >= stagnation_generations:
        #     if self.previous_fitness is not None:
        #         if np.max(self.fitness) - np.max(self.previous_fitness) < stagnation_threshold:
        #             print(f"Стагнация: популяция не изменилась за последние {stagnation_generations} поколений.")
        #             return True

        if self.generation >= self.max_generations:
            self.logger.logger_log.info("Достигнут предел поколений")
            return True

        return False

    def run_generation(self, task_id):
        """Запуск одного поколения алгоритма."""
        self.fitness = self.evaluate_fitness(self.population)
        self.log_process(task_id)
        if self.check_termination_conditions():
            return True

        self.prev_population = self.population
        self.previous_fitness = self.fitness

        # Кроссовер и мутация
        offspring = self.crossover_and_mutate()

        self.population = offspring

        # Адаптация параметров, если задана
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

    def run(self, task_id, task_config):
        """Запуск параллельного генетического алгоритма по всем поколениям."""

        status = Task.Action.FINISHED

        self.logger.logger_log.info(f"[Task id: {task_id}] || started with config: {task_config}")
        self.logger.logger_log.debug("")
        if not DEBUG:
            try:
                self.population = self.initialize_population_function(self)
                if self.termination_kwargs:
                    self.termination_kwargs["start_time"] = time.time()

                for generation in range(self.max_generations):
                    self.generation = generation
                    terminate = self.run_generation(task_id)

                    if terminate:
                        break
            except Exception as error:
                self.logger.logger_log.info(f"[Task id: {task_id}] || Algorithm has {error = }")
                status = Task.Action.ERROR
        else:
            self.population = self.initialize_population_function(self)
            if self.termination_kwargs:
                self.termination_kwargs["start_time"] = time.time()

            for generation in range(self.max_generations):
                self.generation = generation
                terminate = self.run_generation(task_id)

                if terminate:
                    break

        self.logger.logger_log.info(f"[Task id: {task_id}] || finished with status {status}")
        self.finish(task_id, status)

    def log_process(self, task_id):
        min_fitness, min_fitness_individual, max_fitness, max_fitness_individual = self.get_min_max_fitness_individual()

        avg_fitness = self.get_average_fitness()

        self.logger.log(task_id, self.generation,
                        min_fitness, min_fitness_individual,
                        max_fitness, max_fitness_individual,
                        avg_fitness)  # вывести значения лучшего поколения для мин и для макс

    def get_min_max_fitness_individual(self):
        """Возвращает особи с минимальным и максимальным значением фитнес-функции."""

        # Находим индекс особи с минимальным фитнесом
        min_index = np.argmin(self.fitness)
        min_fitness_value = self.fitness[min_index]
        min_fitness_individual = self.population[min_index]

        max_index = np.argmax(self.fitness)
        max_fitness_value = self.fitness[max_index]
        max_fitness_individual = self.population[max_index]

        return min_fitness_value, min_fitness_individual, max_fitness_value, max_fitness_individual

    def get_average_fitness(self):
        """Возвращает среднее значение фитнеса для всей популяции."""
        average_fitness = np.mean(self.fitness)
        return average_fitness

    @staticmethod
    def finish(task_id, status):
        """Завершение алгоритма"""
        task_obj = Task.objects.get(id=task_id)
        task_obj.status = status
        task_obj.save()

        experiment_status = Experiment.Action.FINISHED
        set_experiment_status(task_obj, experiment_status)
