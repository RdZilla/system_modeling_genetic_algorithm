import logging
import json
import os
import datetime

from modeling_system_backend import settings

RESULT_ROOT = settings.RESULT_ROOT

TEXT_LOG_FILE_NAME = "text_log.log"
JSON_LOG_FILE_NAME = "json_log.json"


def get_user_folder_name(user_id):
    return f"user_id-{user_id}"


def get_task_folder_name(task_id):
    return f"task_id-{task_id}"


def get_logger(experiment_name, user_id, task_id):
    """Создаёт и возвращает логгер с динамическим именем файла"""

    # Динамическое имя файла с датой и именем задачи
    user_folder_name = get_user_folder_name(user_id)
    task_folder_name = get_task_folder_name(task_id)
    results_folder_path = os.path.join(RESULT_ROOT, user_folder_name, experiment_name, task_folder_name)

    os.makedirs(results_folder_path, exist_ok=True)

    log_filepath = os.path.join(results_folder_path, TEXT_LOG_FILE_NAME)

    logger = logging.getLogger('experiment')
    logger.setLevel(logging.DEBUG)

    # Удаляем предыдущие обработчики, чтобы избежать дублирования логов
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_filepath)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


class ExperimentLogger:
    """Логирование работы ГА"""

    def __init__(self, experiment_name, user_id, task_id):
        logger = get_logger(experiment_name, user_id, task_id)

        self.logger_log = logger
        self.log_file_json = self.get_json_log_path(logger)

        self.logs = []

    @staticmethod
    def get_json_log_path(logger):
        logger_filepath = logger.handlers[0].baseFilename
        results_folder, _ = os.path.split(logger_filepath)

        json_logger = os.path.join(results_folder, JSON_LOG_FILE_NAME)
        return json_logger

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
