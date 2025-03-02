import importlib

from celery import shared_task
from rest_framework.response import Response

from api.responses import bad_request_response, success_response
from api.utils.custom_logger import ExperimentLogger
from api.utils.load_custom_funcs.UserFunctionMixin import UserFunctionMixin
from api.utils.load_custom_funcs.core_function_utils import SUPPORTED_MODELS_GA
from core.models.asynchronous_model import AsynchronousGA
from core.models.island_model import IslandGA
from core.models.master_worker_model import MasterWorkerGA
from task_modeling.models import Task


def get_function_from_string(path: str):
    """Импортирует функцию по строковому пути."""
    module_name, function_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


@shared_task
def wrapper_run_task(additional_params, functions_params, json_ga, task_id, generations):
    algorithm_type = additional_params.get("algorithm_type")
    task_config = additional_params.get("task_config")

    experiment_name = additional_params.get("experiment_name")
    user_id = additional_params.get("user_id")
    logger = ExperimentLogger(experiment_name, user_id, task_id)

    if algorithm_type == "master_worker":
        ga = MasterWorkerGA.from_json(json_ga)
    else:
        ga = MasterWorkerGA.from_json(json_ga)

    for function_name, function_route in functions_params.items():
        ga_function = get_function_from_string(function_route)
        setattr(ga, function_name, ga_function)
    ga.logger = logger
    return ga.run(task_id, generations, task_config)


def check_usability_function(function_mapping, function_name, function_type, task):
    function_route = function_mapping.get(function_name, None)
    if not function_route:
        task.status = Task.Action.ERROR
        task.save()
        return bad_request_response(f"Invalid {function_type} function")
    return function_route


def run_task(task: Task) -> Response:
    experiment_name = task.experiment.name
    user_id = task.experiment.user_id
    task_id = task.id

    task_config = task.config.config

    algorithm_type = task_config.get("algorithm")

    generations = task_config.get("generations")

    population_size = task_config.get("population_size")
    # selection_function = ...  TODO: add selection_function

    mutation_rate = task_config.get("mutation_rate")
    # mutation_function = ...   TODO: add mutation_function

    crossover_rate = task_config.get("crossover_rate")
    # crossover_function = ...  TODO: add crossover_function

    fitness_function = task_config.get("fitness_function")

    # TODO: Убрать из абстрактного класса абстракцию с методов на селекцию, кроссинговер и мутацию.
    #  Реализовать в абстрактном классе логики селекции, кроссинговера и мутацию и наследовать их в каждом алгоритме

    # TODO: Добавить валидацию данных

    functions_mapping = UserFunctionMixin.get_functions_mapping(user_id)
    if isinstance(functions_mapping, Response):
        return functions_mapping
    crossover_functions, fitness_functions, mutation_functions, selection_functions = functions_mapping

    fitness_function_name = check_usability_function(fitness_functions, fitness_function, "fitness", task)
    if isinstance(fitness_function_name, Response):
        return fitness_function_name

    if algorithm_type not in SUPPORTED_MODELS_GA:
        task.status = Task.Action.ERROR
        task.save()
        return bad_request_response("Invalid algorithm type")

    # try:
    #     ga.run(generations)
    # except Exception as e:
    #     logger.logger_log.error(f"Task {task.id} failed with error: {e}")
    #     response["error"] = str(e)
    #     return response

    task.status = Task.Action.STARTED
    task.save()

    # json_ga = ga.to_json()

    additional_params = {
        "algorithm_type": algorithm_type,
        "experiment_name": experiment_name,
        "user_id": user_id,
        "task_id": task_id,
        "task_config": task_config,
    }

    functions_params = {
        "fitness_function": fitness_function_name
    }

    wrapper_run_task.delay(additional_params, functions_params, json_ga, task_id, generations)
    return success_response(f"Task {task.id} started successfully")
