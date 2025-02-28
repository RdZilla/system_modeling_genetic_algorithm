from core.models.GA_base_model import GeneticAlgorithm
from core.fitness.rastrigin_fitness import rastrigin
import random

class IslandGA:
    def __init__(self, population_size, mutation_rate, crossover_rate, fitness_function_name,
                 num_islands, migration_interval, logger):
        self.num_islands = num_islands
        self.migration_interval = migration_interval
        self.islands = [
            GeneticAlgorithm(population_size, mutation_rate, crossover_rate, fitness_function_name, logger)
            for _ in range(num_islands)
        ]

    def migrate(self):
        """Обмен особями между островами"""
        for i in range(self.num_islands):
            if random.random() < 0.5:  # Случайная миграция
                target = (i + 1) % self.num_islands
                migrant = random.choice(self.islands[i].population)
                self.islands[target].population.append(migrant)

    def run(self, generations):
        """Запуск ГА на каждом острове"""
        for generation in range(generations):
            for island in self.islands:
                island.evolve()
            if generation % self.migration_interval == 0:
                self.migrate()
