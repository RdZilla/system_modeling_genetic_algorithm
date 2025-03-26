from django.contrib.auth.models import User

from api.responses import bad_request_response
from api.utils.load_custom_funcs.core_function_utils import SUPPORTED_MODELS_GA
from core.models.master_worker_model import MasterWorkerGA
from task_modeling.models import TaskConfig


class PrepareTaskConfigMixin:
    order_possible_params = [
        "algorithm",
        "population_size",
        "max_generations",

        "mutation_rate",
        "selection_rate",
        "crossover_rate",

        "num_workers",

        "adaptation_function",
        "adaptation_kwargs",

        "crossover_function",
        "crossover_kwargs",

        "fitness_function",
        "fitness_kwargs",

        "initialize_population_function",
        "initialize_population_kwargs",

        "mutation_function",
        "mutation_kwargs",

        "selection_function",
        "selection_kwargs",

        "termination_function",
        "termination_kwargs",

        "num_islands",
        "migration_interval",
        "migration_rate",
    ]

    @classmethod
    def validate_task_config(
            cls,
            config_name: (str | None),
            task_config: dict,
            partial_check=False
    ) -> (str | None):
        """
        Function for validate task config
        :param config_name: Configuration name requiring validation
        :param task_config: Configuration task requiring validation
        :param partial_check: Partial check
        :return: Configuration that has not passed validation
        """
        if not config_name and not partial_check:
            return "Invalid config name"

        algorithm_type = task_config.get("algorithm")

        ga_model = SUPPORTED_MODELS_GA.get(algorithm_type, None)
        if not ga_model:
            return "Invalid algorithm type"

        required_params = ga_model.REQUIRED_PARAMS

        for required_param in required_params:
            if required_param not in task_config:
                return f"{required_param} is not valid"

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

            error_config = cls.validate_task_config(config_name, task_config)
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
