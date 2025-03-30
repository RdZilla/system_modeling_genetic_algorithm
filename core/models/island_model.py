import copy
import random

import numpy as np

# from multiprocessing import Pool
from billiard.pool import Pool

from api.utils.custom_logger import ExperimentLogger
from core.models.mixin_models.ga_mixin_models import GeneticAlgorithmMixin
from core.models.master_worker_model import MasterWorkerGA


class IslandGA(GeneticAlgorithmMixin):
    REQUIRED_PARAMS = [
        *GeneticAlgorithmMixin.REQUIRED_PARAMS,
        "num_islands",
        "migration_interval",
        "migration_rate",
    ]

    def __init__(self,
                 num_islands,
                 migration_interval,
                 migration_rate,

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

        self.num_islands = num_islands
        self.migration_interval = migration_interval
        self.migration_rate = migration_rate

        self.islands = None
        self.generation = None

    def migrate(self):
        """Функция миграции особей между островами."""
        num_islands = len(self.islands)
        population_size, chrom_length = self.islands[0].population.shape

        migrated_populations = [copy.deepcopy(island.population) for island in self.islands]

        # Количество мигрирующих особей
        num_migrants = max(1, int(population_size * self.migration_rate))
        self.logger.logger_log.info(f"[{self.task_id}] || {num_migrants = }")

        for num_island in range(num_islands):
            next_island = (num_island + 1) % num_islands  # Определяем соседний остров
            population = migrated_populations[num_island]

            # Случайно выбираем индивидов для миграции
            migrant_indices = random.sample(range(population_size), num_migrants)

            migrants = population[migrant_indices]

            # Добавляем мигрантов в популяцию соседнего острова
            self.islands[next_island].population = np.vstack((self.islands[next_island].population, migrants))

            # Удаляем мигрантов из текущего острова
            self.islands[num_island].population = np.delete(self.islands[num_island].population, migrant_indices,
                                                            axis=0)

    def start_calc(self):
        self.init_islands()

        for generation in range(1, self.max_generations + 1):
            self.generation = generation

            for island in self.islands:
                island.generation = generation

            with Pool(self.num_workers) as pool:
                terminate_flags = pool.starmap(MasterWorkerGA.run_generation, [(island,) for island in self.islands])
            self.logger.merge_logs(self.num_islands)

            self.logger.logger_log.info(f"[{self.task_id}] || {terminate_flags = }")

            is_created_log = self.create_result_log()
            if is_created_log:
                break

            if generation % self.migration_interval == 0:
                self.logger.logger_log.info(f"c || Migration between islands")
                self.migrate()
                self.logger.logger_log.info(f"[{self.task_id}] || Migration success")

    def init_islands(self):
        self.islands = []
        for num_island in range(self.num_islands):
            experiment_name = self.logger.experiment_name
            user_id = self.logger.user_id
            task_id = self.logger.task_id
            logger = ExperimentLogger(experiment_name, user_id, task_id)
            logger.set_process_id(num_island)

            island = MasterWorkerGA(
                self.population_size,
                self.max_generations,

                self.mutation_rate,
                self.crossover_rate,

                self.num_workers,

                self.adaptation_function,
                self.adaptation_kwargs,

                self.crossover_function,
                self.crossover_kwargs,

                self.fitness_function,
                self.fitness_kwargs,

                self.initialize_population_function,
                self.initialize_population_kwargs,

                self.mutation_function,
                self.mutation_kwargs,

                self.selection_function,
                self.selection_kwargs,

                self.termination_function,
                self.termination_kwargs,
                logger
            )
            island.population = self.initialize_population_function(self)
            island.task_id = self.task_id
            self.islands.append(island)

    def create_result_log(self):
        for island in self.islands:
            if island.terminate:
                island.logger.create_result_log()
                return True
