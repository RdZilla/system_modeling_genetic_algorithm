import copy
import random

import numpy as np

from celery import shared_task, group

from core.models.mixin_models.ga_mixin_models import GeneticAlgorithmMixin
from core.models.master_worker_model import MasterWorkerGA

@shared_task(ignore_result=True)
def wrapper_run_task(island):
    terminate_flags = island.run_generation()
    return island, terminate_flags

class IslandGA(GeneticAlgorithmMixin):
    REQUIRED_PARAMS = [
        *GeneticAlgorithmMixin.REQUIRED_PARAMS,
        "num_islands",
        "migration_interval",
        "migration_rate",
    ]

    def __init__(self, additional_params, ga_params, functions_routes):
        super().__init__(additional_params, ga_params, functions_routes)

        self.num_islands = int(ga_params.get("num_islands"))
        self.migration_interval = int(ga_params.get("migration_interval"))
        self.migration_rate = float(ga_params.get("migration_rate"))

        self.additional_params = additional_params
        self.ga_params = ga_params
        self.functions_routes = functions_routes

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

            task_group = group(wrapper_run_task.s(island) for island in self.islands)

            # Запускаем группу задач и ждем их завершения
            results = task_group.apply().get(timeout=300, disable_sync_subtasks=False)

            # Обрабатываем результаты
            terminate_flags = []
            for idx, (island_result, terminate_flag) in enumerate(results):
                self.islands[idx] = island_result
                terminate_flags.append(terminate_flag)

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
            island = MasterWorkerGA(self.additional_params, self.ga_params, self.functions_routes)
            island.logger.set_process_id(num_island)
            island.population = self.initialize_population_function(self)
            island.task_id = self.task_id
            self.islands.append(island)

    def create_result_log(self):
        for island in self.islands:
            if island.terminate:
                island.logger.create_result_log()
                return True
