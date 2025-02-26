from django.contrib.auth.models import User

from task_modeling.models import TaskConfig


class PrepareTaskConfigMixin:
    required_params = []
    order_possible_params = []

    @classmethod
    def validate_task_config(
            cls,
            config: dict,
            config_name: (str | None),
            task_config: dict
    ):
        """
        Function for validate task config
        :param config:
        :param config_name:
        :param task_config:
        :return:
        """
        if not config_name:
            return config

        for required_param in cls.required_params:  # TODO: для каждой модели настроить свои требуемые параметры
            if required_param not in task_config:
                return config

    @classmethod
    def order_params_task_config(cls, config: dict):
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

            task_config = TaskConfig.objects.filter(config=task_config).first()
            if task_config:
                existing_config.append(task_config)
            else:
                task_config = TaskConfig.objects.create(
                    name=config_name,
                    config=task_config,
                    user=user
                )
                created_configs.append(task_config)

        if error_configs:
            return error_task_configs, existing_config, error_configs

        return error_task_configs, existing_config, created_configs
