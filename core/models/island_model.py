from multiprocessing import cpu_count

import numpy as np
from billiard.pool import Pool


class IslandGA:
    def __init__(self, num_islands, population_size, max_generations, fitness_function,
                 crossover_function, mutation_function, migration_interval=10, migration_rate=0.1,
                 mutation_rate=0.01, crossover_rate=0.7, selection_rate=0.5, num_workers=None,
                 initialize_population_fn=None, termination_fn=None, adaptation_fn=None, selection_fn=None,
                 fitness_threshold=None, stagnation_threshold=None, stagnation_generations=5):
        """
        num_islands: Количество островов
        population_size: Размер популяции на каждом острове
        max_generations: Максимальное количество поколений
        fitness_function: Функция фитнеса
        crossover_function: Функция кроссовера
        mutation_function: Функция мутации
        migration_interval: Частота миграции (в поколениях)
        migration_rate: Процент популяции, участвующий в миграции
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
        """
        self.num_islands = num_islands
        self.population_size = population_size
        self.max_generations = max_generations
        self.fitness_function = fitness_function
        self.crossover_function = crossover_function
        self.mutation_function = mutation_function
        self.migration_interval = migration_interval
        self.migration_rate = migration_rate
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

        # Инициализация островов
        self.islands = [self.initialize_population_fn() for _ in range(self.num_islands)]

    def default_initialize_population(self):
        """Инициализирует популяцию случайными хромосомами (по умолчанию)."""
        return np.random.rand(self.population_size, 10)

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы в популяции с использованием Celery."""
        with Pool(processes=self.num_workers) as pool:
            fitness_values = pool.map(self.fitness_function, population)
        return np.array(fitness_values)

    def default_selection_fn(self, population, fitness):
        """Стандартная функция селекции — турнирная."""
        indices = np.random.choice(len(population), size=self.population_size, replace=True)
        return population[indices]

    def migrate(self):
        """Миграция между островами."""
        num_migrants = int(self.population_size * self.migration_rate)
        migrants = []

        # Выбор мигрантов с каждого острова
        for island in self.islands:
            indices = np.random.choice(len(island), num_migrants, replace=False)
            migrants.append(island[indices])

        # Перемешиваем мигрантов и отправляем их на следующие острова
        for i in range(self.num_islands):
            next_island = (i + 1) % self.num_islands
            self.islands[next_island][:num_migrants] = migrants[i]

    def run_island(self, island, generation):
        """Запуск одного поколения для острова."""
        fitness = self.evaluate_fitness(island)
        mating_pool = self.selection_fn(island, fitness)
        offspring = self.crossover_and_mutate(mating_pool)
        return offspring

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

    def run(self):
        """Запуск островной модели ГА."""
        for generation in range(self.max_generations):
            print(f"Generation {generation}")

            # Обрабатываем каждый остров параллельно
            with Pool(self.num_workers) as pool:
                results = pool.starmap(self.run_island, [(island, generation) for island in self.islands])

            # Обновляем популяции островов
            self.islands = results

            # Миграция каждые migration_interval поколений
            if generation % self.migration_interval == 0:
                self.migrate()

            # Проверяем условия завершения для каждого острова
            for island in self.islands:
                fitness = self.evaluate_fitness(island)
                if self.termination_fn and self.termination_fn(generation, fitness):
                    print("Пользовательская функция завершения остановила алгоритм.")
                    return self.islands, fitness

        return self.islands