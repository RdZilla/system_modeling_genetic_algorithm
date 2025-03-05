from multiprocessing import cpu_count

import numpy as np
from billiard.pool import Pool

from task_modeling.models import Experiment, Task


class MasterWorkerGA:
    def __init__(self, population_size, max_generations, fitness_function, crossover_function, mutation_function,
                 mutation_rate=0.01, crossover_rate=0.7, selection_rate=0.5, num_workers=None,
                 initialize_population_fn=None, termination_fn=None, adaptation_fn=None, selection_fn=None,
                 fitness_threshold=None, stagnation_threshold=None, stagnation_generations=5, logger=None):
        """
        population_size: Размер популяции
        max_generations: Максимальное количество поколений
        fitness_function: Функция фитнеса
        crossover_function: Функция кроссовера
        mutation_function: Функция мутации
        mutation_rate: Вероятность мутации
        crossover_rate: Вероятность кроссовера
        selection_rate: Вероятность селекции
        num_workers: Количество рабочих процессов для параллельных вычислений
        initialize_population_fn: Функция для инициализации популяции
        termination_fn: Функция завершения алгоритма
        adaptation_fn: Функция адаптации параметров
        selection_fn: Функция селекции
        fitness_threshold: Пороговое значение для фитнеса, при котором алгоритм завершится
        stagnation_threshold: Порог для изменения фитнеса
        stagnation_generations: Количество поколений без улучшений для прекращения работы
        logger: Объект ExperimentLogger для логирования процесса
        """
        # Параметры генетического алгоритма
        self.population_size = population_size
        self.max_generations = max_generations
        self.fitness_function = fitness_function
        self.crossover_function = crossover_function
        self.mutation_function = mutation_function
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.selection_rate = selection_rate
        self.num_workers = num_workers or cpu_count()

        # Пользовательские функции
        self.initialize_population_fn = initialize_population_fn or self.default_initialize_population
        self.termination_fn = termination_fn
        self.adaptation_fn = adaptation_fn
        self.selection_fn = selection_fn or self.default_selection_fn

        # Условия завершения
        self.fitness_threshold = fitness_threshold
        self.stagnation_threshold = stagnation_threshold
        self.stagnation_generations = stagnation_generations

        # Инициализация популяции
        self.population = self.initialize_population_fn()
        self.previous_fitness = None
        self.logger = logger

    def default_initialize_population(self):
        """Инициализирует популяцию случайными хромосомами (по умолчанию)."""
        return np.random.rand(self.population_size, 10)

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы в популяции с использованием Celery."""
        with Pool(processes=self.num_workers) as pool:
            fitness_values = pool.map(self.fitness_function, population)
        return np.array(fitness_values)

    def default_selection_fn(self, population):
        """Стандартная функция селекции — турнирная."""
        indices = np.random.choice(len(population), size=self.population_size, replace=True)
        return population[indices]

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
        mating_pool = self.selection_fn(self.population)

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

    def run(self, task_id, generations, task_config):
        """Запуск параллельного генетического алгоритма по всем поколениям."""

        self.logger.logger_log.info(f"[Task id: {task_id}] || started with config: {task_config}")

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
