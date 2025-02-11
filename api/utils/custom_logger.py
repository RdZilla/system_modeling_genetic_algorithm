import logging
import json
import os
import datetime

from modeling_system_backend import settings

LOG_ROOT = settings.LOG_ROOT


def get_logger(experiment_name, task_config_id):
    """Создаёт и возвращает логгер с динамическим именем файла"""

    today_timestamp = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
    experiment_stamp = f"{experiment_name}__config-{task_config_id}__{today_timestamp}"

    # Динамическое имя файла с датой и именем задачи
    log_filename = f"{experiment_stamp}.log"
    log_filepath = os.path.join(LOG_ROOT, log_filename)

    logger = logging.getLogger('experiment')
    logger.setLevel(logging.DEBUG)

    # Удаляем предыдущие обработчики, чтобы избежать дублирования логов
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создаём обработчик для записи в файл
    # open(log_filepath, 'a').close()
    file_handler = logging.FileHandler(log_filepath)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


class ExperimentLogger:
    """Логирование работы ГА"""

    def __init__(self, experiment_name, task_config_id):
        today_timestamp = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
        experiment_stamp = f"{experiment_name}__conf_{task_config_id}__{today_timestamp}"

        logger = get_logger(experiment_name, task_config_id)
        logger_filepath = logger.handlers[0].baseFilename
        root_path, log_filename = os.path.split(logger_filepath)

        # new_log_filename_log = f"{log_filename.replace('.log', '')}_{experiment_stamp}.log"
        # new_log_filepath_log = os.path.join(root_path, new_log_filename_log)
        #
        # logger.handlers[0].namer = new_log_filepath_log

        self.logger_log = logger

        self.log_file_json = os.path.join(root_path, f"{experiment_stamp}.json")

        self.logs = []

    def log(self, generation, best_fitness, avg_fitness):
        """Логирование данных о поколении"""
        entry = {
            "generation": generation,
            "best_fitness": best_fitness,
            "avg_fitness": avg_fitness,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.logger_log.info(f"Generation {generation}: Best fitness = {best_fitness}")

        self.logs.append(entry)
        with open(self.log_file_json, "w") as f:
            json.dump(self.logs, f, indent=4)

    def get_logs(self):
        """Получение всех логов"""
        return self.logs
