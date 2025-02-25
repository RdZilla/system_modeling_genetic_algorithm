import logging
import json
import os
import datetime

from modeling_system_backend import settings

RESULT_ROOT = settings.RESULT_ROOT
TXT_FOLDER = "txt"
JSON_FOLDER = "json"
CSV_FOLDER = "csv"
PNG_FOLDER = "png"


def get_logger(experiment_name, task_config_id, user_id, task_model):
    """Создаёт и возвращает логгер с динамическим именем файла"""

    today_timestamp = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    experiment_stamp = f"{experiment_name}__config-{task_config_id}__{today_timestamp}"

    # Динамическое имя файла с датой и именем задачи
    log_filename = f"{experiment_stamp}.log"  # user/task_name/timestamp/model_ga_name
    user_folder_name = f"user_id-{user_id}"
    user_folder_path = os.path.join(RESULT_ROOT, user_folder_name)
    task_folder_path = os.path.join(user_folder_path)
    timestamp_folder_path = os.path.join(task_folder_path, today_timestamp)
    ga_model_folder_path = os.path.join(timestamp_folder_path, task_model)

    os.makedirs(ga_model_folder_path, exist_ok=True)

    log_filepath = os.path.join(ga_model_folder_path, log_filename)

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

    def __init__(self, experiment_name, task_config_id, user_folder, task_model):
        logger = get_logger(experiment_name, task_config_id, user_folder, task_model)

        self.logger_log = logger
        self.log_file_json = self.get_json_log_path(logger)

        self.logs = []

    @staticmethod
    def get_json_log_path(logger):
        logger_filepath = logger.handlers[0].baseFilename
        log_path, log_filename = os.path.split(logger_filepath)

        json_log_name = log_filename.replace(".log", ".json")
        json_logger = os.path.join(log_path, f"{json_log_name}.json")
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
