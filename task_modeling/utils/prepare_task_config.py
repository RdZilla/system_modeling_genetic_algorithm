from django.contrib.auth.models import User

from core.models.master_worker_model import MasterWorkerGA
from task_modeling.models import TaskConfig


class PrepareTaskConfigMixin:
    order_possible_params = [
        "algorithm",
        "generations",
        "population_size",
        "selection_function",
        "mutation_rate",
        "mutation_function",
        "crossover_rate",
        "crossover_function",
        "fitness_function",
    ]

    @classmethod
    def validate_task_config(
            cls,
            config: dict,
            config_name: (str | None),
            task_config: dict,
            partial_check=False
    ) -> (dict | None):
        """
        Function for validate task config
        :param config: Configuration requiring validation
        :param config_name: Configuration name requiring validation
        :param task_config: Configuration task requiring validation
        :param partial_check: Partial check
        :return: Configuration that has not passed validation
        """
        if not config_name and not partial_check:
            return config
        algorithm_type = task_config.get("algorithm")
        match algorithm_type:
            case "master_worker":
                required_params = MasterWorkerGA.required_params
            case _:
                return config
        for required_param in required_params:
            if required_param not in task_config:
                return config

    @classmethod
    def order_params_task_config(cls, config: dict) -> dict:
        """
        Function for ordering task config.\n
        It's necessary to eliminate duplicates in TaskConfig model.
        :param config: Config of the future task
        :return: ordered config
        """

        ordered_config = {param: config[param] for param in cls.order_possible_params if param in config}
        return ordered_config

    @classmethod
    def get_or_create_task_config(cls, configs: list, user: User) -> [bool, list]:
        error_task_configs = False

        error_configs = []
        existing_config = []
        created_configs = []

        for config in configs:
            config_name = config.get("name", None)
            task_config = config.get("config", {})

            error_config = cls.validate_task_config(config, config_name, task_config)
            if error_config:
                error_task_configs = True
                error_configs.append(error_config)
                continue

            task_config = cls.order_params_task_config(task_config)

            task_config_obj = TaskConfig.objects.filter(config=task_config, user=user).first()
            if task_config_obj:
                existing_config.append(task_config_obj)
            else:
                task_config_obj = TaskConfig.objects.create(
                    name=config_name,
                    config=task_config,
                    user=user
                )
                created_configs.append(task_config_obj)

        if error_configs:
            return error_task_configs, existing_config, error_configs

        return error_task_configs, existing_config, created_configs
