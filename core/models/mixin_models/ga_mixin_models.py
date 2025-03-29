import time
import traceback
from abc import abstractmethod
from multiprocessing import cpu_count

import numpy as np

from task_modeling.models import Task, Experiment
from task_modeling.utils.set_experiment_status import set_experiment_status


class LogResultMixin:
    def log_process(self, task_id, generation, population, fitness):
        (min_fitness, min_fitness_individual,
         max_fitness, max_fitness_individual) = self.get_min_max_fitness_individual(population, fitness)

        avg_fitness = self.get_average_fitness(fitness)

        self.logger.log(task_id, generation,
                        min_fitness, min_fitness_individual,
                        max_fitness, max_fitness_individual,
                        avg_fitness)  # вывести значения лучшего поколения для мин и для макс

    @staticmethod
    def get_min_max_fitness_individual(population, fitness):
        """Возвращает особи с минимальным и максимальным значением фитнес-функции."""

        # Находим индекс особи с минимальным фитнесом
        min_index = np.argmin(fitness)
        min_fitness_value = fitness[min_index]
        min_fitness_individual = population[min_index]

        max_index = np.argmax(fitness)
        max_fitness_value = fitness[max_index]
        max_fitness_individual = population[max_index]

        return min_fitness_value, min_fitness_individual, max_fitness_value, max_fitness_individual

    @staticmethod
    def get_average_fitness(fitness):
        """Возвращает среднее значение фитнеса для всей популяции."""
        average_fitness = np.mean(fitness)
        return average_fitness

class GeneticAlgorithmMixin(LogResultMixin):

    REQUIRED_PARAMS = [
        "algorithm",
        "population_size",
        "max_generations",

        "mutation_rate",
        "crossover_rate",

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

        num_workers: Количество рабочих процессов для параллельных вычислений

        adaptation_function: Функция адаптации параметров
        adaptation_kwargs: Параметры функции адаптации

        crossover_function: Функция кроссовера
        crossover_kwargs: Параметры функции кроссовера

        fitness_function: Функция фитнеса
        fitness_kwargs: Параметры функции фитнеса

        initialize_population_function: Функция для инициализации популяции
        initialize_population_kwargs: Параметры функции для инициализации популяции

        mutation_function: Функция мутации
        mutation_kwargs: Параметры функции мутации

        selection_function: Функция селекции
        selection_kwargs: Параметры функции селекции

        termination_function: Функция завершения алгоритма
        termination_kwargs: Параметры функции завершения алгоритма

        logger: Объект ExperimentLogger для логирования процесса
        """
        # Параметры генетического алгоритма
        self.population_size = population_size
        self.max_generations = max_generations

        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

        self.num_workers = num_workers or cpu_count()

        # Пользовательские функции
        self.adaptation_function = adaptation_function
        self.adaptation_kwargs = adaptation_kwargs

        self.crossover_function = crossover_function
        self.crossover_kwargs = crossover_kwargs

        self.fitness_function = fitness_function
        self.fitness_kwargs = fitness_kwargs

        self.initialize_population_function = initialize_population_function
        self.initialize_population_kwargs = initialize_population_kwargs

        self.mutation_function = mutation_function
        self.mutation_kwargs = mutation_kwargs

        self.selection_function = selection_function
        self.selection_kwargs = selection_kwargs

        self.termination_function = termination_function
        self.termination_kwargs = termination_kwargs

        self.logger = logger

        self.task_id = None

    @abstractmethod
    def start_calc(self):
        pass

    def run(self, task_id, task_config):
        """Запуск параллельного генетического алгоритма по всем поколениям."""

        self.task_id = task_id

        status = Task.Action.FINISHED
        start_time = time.time()
        self.logger.logger_log.info(f"[{task_id}] || started with config: {task_config}")
        self.logger.logger_log.info(f"[{task_id}] || Start time: {start_time}")
        self.logger.logger_log.debug("")

        if self.termination_kwargs:
            self.termination_kwargs["start_time"] = start_time
            self.termination_kwargs["stagnation_generation_count"] = 0

        try:
            self.start_calc()
        except Exception as error:
            self.logger.logger_log.error(f"[Task id: {task_id}] || Algorithm has {error = }")
            self.logger.logger_log.error(traceback.format_exc())

            status = Task.Action.ERROR

        finish_time = time.time()
        self.logger.logger_log.info(f"[{task_id}] || finished with status {status}")
        self.logger.logger_log.info(f"[{task_id}] || Finish time: {finish_time}")

        execution_time = finish_time - start_time
        self.logger.logger_log.info(f"[{task_id}] || Execution time: {execution_time}")
        self.logger.logger_log.debug("")

        self.finish(task_id, status)

    @staticmethod
    def finish(task_id, status):
        """Завершение алгоритма"""
        task_obj = Task.objects.get(id=task_id)
        task_obj.status = status
        task_obj.save()

        experiment_status = Experiment.Action.FINISHED
        set_experiment_status(task_obj, experiment_status)

        if status == Task.Action.ERROR:
            raise RuntimeError
