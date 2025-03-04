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
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin


def get_function_from_string(path: str):
    """Импортирует функцию по строковому пути."""
    module_name, function_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


@shared_task
def wrapper_run_task(additional_params, ga_params, functions_routes, task_id):
    algorithm_type = additional_params.get("algorithm_type")
    task_config = additional_params.get("task_config")
    experiment_name = additional_params.get("experiment_name")
    user_id = additional_params.get("user_id")
    logger = ExperimentLogger(experiment_name, user_id, task_id)

    if algorithm_type == "master_worker":
        ga = MasterWorkerGA
    else:
        ga = MasterWorkerGA

    ga = ga(**ga_params)

    for function_name, function_route in functions_routes.items():
        ga_function = get_function_from_string(function_route)
        setattr(ga, function_name, ga_function)
    ga.logger = logger
    return ga.run(task_id, task_config)


def check_usability_function(functions_params, functions_mapping, task):
    (adaptation_functions,
     crossover_functions,
     fitness_functions,
     init_population_functions,
     mutation_functions,
     selection_functions,
     termination_functions) = functions_mapping

    functions_routes = {}

    for function_type, function_name in functions_params.items():
        match function_type:
            case "adaptation_function":
                function_mapping = adaptation_functions
            case "crossover_function":
                function_mapping = crossover_functions
            case "fitness_function":
                function_mapping = fitness_functions
            case "initialize_population_function":
                function_mapping = init_population_functions
            case "mutation_function":
                function_mapping = mutation_functions
            case "selection_function":
                function_mapping = selection_functions
            case "termination_function":
                function_mapping = termination_functions
            case _:
                task.status = Task.Action.ERROR
                task.save()
                return bad_request_response(f"Unsupported {function_type =}")

        if function_type not in MasterWorkerGA.REQUIRED_PARAMS:
            continue
        function_route = function_mapping.get(function_name, None)

        if not function_route:
            task.status = Task.Action.ERROR
            task.save()
            return bad_request_response(f"Invalid {function_type} function: {function_name} not found")

        functions_routes[function_type] = function_route

    return functions_routes


def run_task(task: Task) -> Response:
    experiment_name = task.experiment.name
    user_id = task.experiment.user_id
    task_id = task.id

    task_config = task.config.config

    algorithm_type = task_config.get("algorithm")

    validate_config = {}

    validate_result = PrepareTaskConfigMixin.validate_task_config(validate_config,
                                                                  None,
                                                                  task_config,
                                                                  partial_check=True)
    if validate_result:
        return bad_request_response("Error in validate task config")

    additional_params = {
        "experiment_name": experiment_name,
        "user_id": user_id,
        "task_id": task_id,
        "task_config": task_config,
        "algorithm_type": algorithm_type,
    }

    ga_params = {
        "population_size": task_config.get("population_size"),
        "chrom_length": task_config.get("chrom_length"),
        "max_generations": task_config.get("max_generations"),

        "num_workers": task_config.get("num_workers"),

        "fitness_threshold": task_config.get("fitness_threshold"),
        "stagnation_threshold": task_config.get("stagnation_threshold"),
        "stagnation_generations": task_config.get("stagnation_generations"),

        # Вероятности
        "mutation_rate": task_config.get("mutation_rate"),
        "crossover_rate": task_config.get("crossover_rate"),
        "selection_rate": task_config.get("selection_rate"),
    }

    # Названия вычислительных функций
    functions_params = {
        "adaptation_function": task_config.get("adaptation_function"),
        "crossover_function": task_config.get("crossover_function"),
        "fitness_function": task_config.get("fitness_function"),
        "initialize_population_function": task_config.get("initialize_population_function"),
        "mutation_function": task_config.get("mutation_function"),
        "selection_function": task_config.get("selection_function"),
        "termination_function": task_config.get("termination_function"),
    }

    functions_mapping = UserFunctionMixin.get_functions_mapping(user_id)
    if isinstance(functions_mapping, Response):
        return functions_mapping

    functions_routes = check_usability_function(functions_params, functions_mapping, task)
    if isinstance(functions_routes, Response):
        return functions_routes

    if algorithm_type not in SUPPORTED_MODELS_GA:
        task.status = Task.Action.ERROR
        task.save()
        return bad_request_response("Invalid algorithm type")

    task.status = Task.Action.STARTED
    task.save()

    wrapper_run_task(additional_params, ga_params, functions_routes, task_id)
    # wrapper_run_task.delay(additional_params, ga_params, functions_routes, task_id)
    return success_response(f"Task {task.id} started successfully")
