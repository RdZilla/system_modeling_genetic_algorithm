from multiprocessing import cpu_count

import numpy as np
from billiard.pool import Pool

from core.init_population.random_initialization import random_initialization
from core.selection.tournament_selection import tournament_selection
from task_modeling.models import Task, Experiment


class MasterWorkerGA:
    REQUIRED_PARAMS = [
        "algorithm",
        "population_size",
        "chrom_length",
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
        "termination_function"
    ]

    def __init__(self,
                 population_size,
                 chrom_length,
                 max_generations,

                 mutation_rate,
                 crossover_rate,
                 selection_rate,

                 num_workers=None,

                 adaptation_function=None,
                 crossover_function=None,
                 fitness_function=None,
                 initialize_population_function=None,
                 mutation_function=None,
                 selection_function=None,
                 termination_function=None,

                 fitness_threshold=None,
                 stagnation_threshold=None,
                 stagnation_generations=5,
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
        self.chrom_length = chrom_length
        self.max_generations = max_generations

        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.selection_rate = selection_rate

        self.num_workers = num_workers or cpu_count()

        # Пользовательские функции
        self.adaptation_fn = adaptation_function
        self.crossover_function = crossover_function
        self.fitness_function = fitness_function
        self.initialize_population_fn = initialize_population_function or random_initialization
        self.mutation_function = mutation_function
        self.selection_fn = selection_function or tournament_selection
        self.termination_fn = termination_function

        # Условия завершения
        self.fitness_threshold = fitness_threshold
        self.stagnation_threshold = stagnation_threshold
        self.stagnation_generations = stagnation_generations

        self.logger = logger

        self.population = None
        self.previous_fitness = None

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы в популяции с использованием Celery."""
        with Pool(processes=self.num_workers) as pool:
            fitness_values = pool.map(self.fitness_function, population)
        return np.array(fitness_values)

    def check_termination_conditions(self, generation, fitness):
        """Проверка условий завершения алгоритма."""
        if self.termination_fn:
            if self.termination_fn(generation, fitness):
                print("Пользовательская функция завершения остановила алгоритм.")
                return True

        if self.fitness_threshold is not None and np.max(fitness) >= self.fitness_threshold:
            print(f"Порог фитнеса достигнут: {np.max(fitness)}")
            return True

        if self.stagnation_threshold is not None and generation >= self.stagnation_generations:
            if self.previous_fitness is not None:
                if np.max(fitness) - np.max(self.previous_fitness) < self.stagnation_threshold:
                    print(f"Стагнация: популяция не изменилась за последние {self.stagnation_generations} поколений.")
                    return True

        if generation >= self.max_generations:
            print("Достигнут предел поколений.")
            return True

        return False

    def run_generation(self, generation):
        """Запуск одного поколения алгоритма."""
        print(f"Generation {generation}")

        fitness = self.evaluate_fitness(self.population)

        if self.check_termination_conditions(generation, fitness):
            return self.population, fitness, True

        # Селекция с использованием пользовательской функции
        mating_pool = np.array([self.selection_fn(self.population, fitness) for _ in range(len(self.population))])

        # Кроссовер и мутация
        offspring = self.crossover_and_mutate(mating_pool)

        # Адаптация параметров, если задана
        if self.adaptation_fn:
            self.adaptation_fn(self)

        self.population = offspring
        self.previous_fitness = fitness

        return self.population, fitness, False

    def crossover_and_mutate(self, mating_pool):
        """Проводит кроссовер и мутацию на основе вероятностей событий."""
        offspring = []
        for individual in mating_pool:
            if np.random.rand() < self.crossover_rate:
                partner = mating_pool[np.random.randint(len(mating_pool))]
                child1, child2 = self.crossover_function(individual, partner)
            else:
                child1, child2 = individual.copy(), individual.copy()

            if np.random.rand() < self.mutation_rate:
                child1 = self.mutation_function(child1)
            if np.random.rand() < self.mutation_rate:
                child2 = self.mutation_function(child2)

            offspring.extend([child1, child2])
        return np.array(offspring)

    def run(self, task_id, task_config):
        """Запуск параллельного генетического алгоритма по всем поколениям."""

        self.logger.logger_log.info(f"[Task id: {task_id}] || started with config: {task_config}")
        self.population = self.initialize_population_fn(self.population_size, self.chrom_length)

        for generation in range(self.max_generations):
            self.population, fitness, terminate = self.run_generation(generation)

            best_fitness = max(fitness)
            avg_fitness = sum(fitness) / len(fitness)

            self.logger.log(task_id, generation, best_fitness, avg_fitness)

            if terminate:
                self.finish(task_id)
                self.logger.logger_log.info("Algorithm finished successfully")

    @staticmethod
    def finish(task_id):
        """Завершение алгоритма"""
        task_obj = Task.objects.get(id=task_id)
        task_obj.status = Task.Action.FINISHED
        task_obj.save()

        experiment_obj = task_obj.experiment

        experiment_status = Experiment.Action.FINISHED

        related_tasks = Task.objects.filter(
            experiment=experiment_obj,
        )
        stopped_related_tasks = related_tasks.filter(status=Task.Action.STOPPED)
        running_related_tasks = related_tasks.filter(status=Task.Action.STARTED)
        error_related_tasks = related_tasks.filter(status=Task.Action.ERROR)
        if stopped_related_tasks:
            experiment_status = Experiment.Action.STOPPED
        if running_related_tasks:
            experiment_status = Experiment.Action.STARTED
        if error_related_tasks:
            experiment_status = Experiment.Action.ERROR
        experiment_obj.status = experiment_status
        experiment_obj.save()
