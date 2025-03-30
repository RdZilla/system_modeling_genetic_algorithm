import logging
import json
import os
import datetime

from modeling_system_backend import settings

RESULT_ROOT = settings.RESULT_ROOT

TEXT_LOG_FILE_NAME = "text_log.log"
JSON_LOG_FILE_NAME = "json_log.json"

CSV_RESULT_FILE_NAME = "best_csv.csv"
ALL_CSV_RESULTS_FILE_NAME = "all_worker_csv.csv"

BEST_PLOT_FILE_NAME = "best_plot.png"
ALL_RESULTS_PLOT_FILE_NAME = "all_worker_plot.png"

RESULT_KEY = "results"

def get_user_folder_name(user_id) -> str:
    return f"user_id-{user_id}"


def get_task_folder_name(task_id) -> str:
    return f"task_id-{task_id}"


def get_logger(experiment_name: str, user_id, task_id):
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
        self.experiment_name = experiment_name
        self.user_id = user_id
        self.task_id = task_id

        logger = get_logger(experiment_name, user_id, task_id)

        self.logger_log = logger
        self.log_file_json = self.get_json_log_path(logger)

        self.logs = {}

        self._process_id = None

    @staticmethod
    def get_json_log_path(logger):
        logger_filepath = logger.handlers[0].baseFilename
        results_folder, _ = os.path.split(logger_filepath)

        json_logger = os.path.join(results_folder, JSON_LOG_FILE_NAME)
        if os.path.exists(json_logger):
            os.remove(json_logger)
        files_in_folder = os.listdir(results_folder)
        for file in files_in_folder:
            if file.endswith(".tmp"):
                os.remove(os.path.join(results_folder, file))
        return json_logger

    def log(self, task_id, generation, min_fitness, min_fitness_individual,
            max_fitness, max_fitness_individual,
            avg_fitness):
        """Логирование данных о поколении"""

        self.logger_log.info(f"[{task_id}/{self._process_id}] || Generation {generation}:")
        self.logger_log.info(
            f"[{task_id}/{self._process_id}] || Min fitness = {min_fitness}, Individual = {min_fitness_individual}")
        self.logger_log.info(
            f"[{task_id}/{self._process_id}] || Max fitness = {max_fitness}, Individual = {max_fitness_individual}")
        self.logger_log.info(f"[{task_id}/{self._process_id}] || Average fitness = {avg_fitness}")
        self.logger_log.debug("")

        entry = {
            "generation": generation,
            "min_fitness": min_fitness,
            "max_fitness": max_fitness,
            "avg_fitness": avg_fitness,
            "timestamp": datetime.datetime.now().isoformat()
        }

        process_key = f"process_{self._process_id}"

        temp_path_file = f"{self.log_file_json}_{process_key}.tmp"
        if os.path.exists(temp_path_file) and os.path.getsize(temp_path_file) > 0:
            with open(temp_path_file, "r") as json_file:
                self.logs = json.load(json_file)
        else:
            self.logs = {}

        if process_key not in self.logs:
            self.logs[process_key] = []
        self.logs[process_key].append(entry)

        with open(temp_path_file, "w") as json_file:
            json.dump(self.logs, json_file, indent=4)

    def merge_logs(self, process_count):
        full_log = {}

        for process_key in range(process_count):
            process_key_name = f"process_{process_key}"
            temp_path_file = f"{self.log_file_json}_{process_key_name}.tmp"
            if os.path.exists(temp_path_file) and os.path.getsize(temp_path_file) > 0:
                with open(temp_path_file, "r") as json_file:
                    process_log = json.load(json_file)
            else:
                process_log = {}

            process_log_data = process_log.get(process_key_name, [])
            full_log[process_key_name] = process_log_data

        with open(self.log_file_json, "w") as json_file:
            json.dump(full_log, json_file, indent=4)

    def create_result_log(self):
        process_key_name = f"process_{self._process_id}"

        with open(self.log_file_json, "r") as json_file:
            process_log = json.load(json_file)

        process_data = process_log.get(process_key_name)
        process_log[RESULT_KEY] = process_data

        with open(self.log_file_json, "w") as json_file:
            json.dump(process_log, json_file, indent=4)

    def get_logs(self):
        """Получение всех логов"""
        if os.path.exists(self.log_file_json):
            with open(self.log_file_json, "r") as f:
                self.logs = json.load(f)
        else:
            self.logs = {}

    def get_process_id(self):
        return self._process_id

    def set_process_id(self, process_id):
        self._process_id = process_id
