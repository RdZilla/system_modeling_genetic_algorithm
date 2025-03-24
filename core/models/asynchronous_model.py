import numpy as np
from celery import shared_task
from redis.asyncio import lock


class AsynchronousGA:
    def __init__(self, num_islands, population_size, max_generations, fitness_function,
                 crossover_function, mutation_function, migration_rate=0.1,
                 mutation_rate=0.01, crossover_rate=0.7,
                 initialize_population_fn=None, termination_fn=None, adaptation_fn=None, selection_fn=None,
                 fitness_threshold=None, stagnation_threshold=None, stagnation_generations=5):
        """
        num_islands: Количество островов (или процессов)
        population_size: Размер популяции на каждом острове
        max_generations: Максимальное количество поколений
        fitness_function: Функция фитнеса
        crossover_function: Функция кроссовера
        mutation_function: Функция мутации
        migration_rate: Процент популяции для миграции
        mutation_rate: Вероятность мутации
        crossover_rate: Вероятность кроссовера
        initialize_population_fn: Функция для инициализации популяции
        termination_fn: Функция завершения
        adaptation_fn: Функция адаптации параметров
        selection_fn: Функция селекции
        fitness_threshold: Пороговое значение для фитнеса
        """
        self.num_islands = num_islands
        self.population_size = population_size
        self.max_generations = max_generations
        self.fitness_function = fitness_function
        self.crossover_function = crossover_function
        self.mutation_function = mutation_function
        self.migration_rate = migration_rate
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

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

    def migrate(self, island_index):
        """Асинхронная миграция между островами."""
        with lock:
            num_migrants = int(self.population_size * self.migration_rate)
            source_island = self.islands[island_index]
            target_island = self.islands[(island_index + 1) % self.num_islands]
            indices = np.random.choice(len(source_island), num_migrants, replace=False)
            migrants = source_island[indices]
            target_island[:num_migrants] = migrants

    def evaluate_fitness(self, population):
        """Оценка фитнеса для каждой хромосомы."""
        return np.array([self.fitness_function(ind) for ind in population])

    def run_island(self, island_index):
        """Асинхронный запуск ГА на одном острове."""
        island = self.islands[island_index]
        for generation in range(self.max_generations):
            fitness = self.evaluate_fitness(island)
            if self.termination_fn and self.termination_fn(generation, fitness):
                print(f"Остров {island_index}: Завершение по пользовательской функции.")
                return island, fitness

            # Селекция, кроссовер и мутация
            mating_pool = self.selection_fn(island, fitness)
            offspring = self.crossover_and_mutate(mating_pool)

            # Обновление популяции
            self.islands[island_index] = offspring

            # Миграция
            if np.random.rand() < self.migration_rate:
                self.migrate(island_index)

        return self.islands[island_index]

    def crossover_and_mutate(self, mating_pool):
        """Кроссовер и мутация."""
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
        """Запуск асинхронной модели ГА."""
        tasks = [async_run_island.delay(self, i) for i in range(self.num_islands)]
        results = [task.get() for task in tasks]
        return results

@shared_task
def async_run_island(ga_instance, island_index):
    """Асинхронная задача для запуска ГА на острове."""
    return ga_instance.run_island(island_index)
