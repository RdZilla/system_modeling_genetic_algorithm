import importlib

from celery import shared_task
from rest_framework.response import Response

from api.responses import bad_request_response, success_response
from api.utils.custom_logger import ExperimentLogger
from api.utils.load_custom_funcs.UserFunctionMixin import UserFunctionMixin
from api.utils.load_custom_funcs.core_function_utils import SUPPORTED_MODELS_GA
from task_modeling.models import Task, Experiment
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.utils.set_experiment_status import set_experiment_status


@shared_task
def wrapper_run_task(additional_params, ga_params, functions_routes):
    algorithm_type = additional_params.get("algorithm_type")
    task_config = additional_params.get("task_config")
    task_config.update({**functions_routes})
    task_id = additional_params.get("task_id")

    ga = SUPPORTED_MODELS_GA[algorithm_type]
    ga = ga(additional_params, ga_params, functions_routes)
    return ga.run(task_id, task_config)


def check_usability_function(algorithm_type, functions_params, functions_mapping, task):
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

        ga_model = SUPPORTED_MODELS_GA[algorithm_type]
        function_route = function_mapping.get(function_name, None)

        if not function_route:
            if function_type in ga_model.REQUIRED_PARAMS:
                task.status = Task.Action.ERROR
                task.save()
                return bad_request_response(f"Invalid {function_type} function: {function_name} not found")
            continue

        functions_routes[function_type] = function_route

    return functions_routes


def run_task(task: Task) -> Response:
    experiment_name = task.experiment.name
    user_id = task.experiment.user_id
    task_id = task.id

    task_config = task.config.config

    validate_result = PrepareTaskConfigMixin.validate_task_config(None,
                                                                  task_config,
                                                                  partial_check=True)
    if validate_result:
        task.status = Task.Action.ERROR
        task.save()
        return bad_request_response(f"Ошибка валидации конфигурации: {validate_result}")

    algorithm_type = task_config.pop("algorithm")

    additional_params = {
        "experiment_name": experiment_name,
        "user_id": user_id,
        "task_id": task_id,
        "task_config": task_config,
        "algorithm_type": algorithm_type,
    }

    function_keys = [
        "adaptation_function",
        "crossover_function",
        "fitness_function",
        "initialize_population_function",
        "mutation_function",
        "selection_function",
        "termination_function",
    ]
    functions_params = {}
    for function_key in function_keys:
        functions_params[function_key] = task_config.pop(function_key, None)

    functions_mapping = UserFunctionMixin.get_functions_mapping(user_id)
    if isinstance(functions_mapping, Response):
        task.status = Task.Action.ERROR
        task.save()
        return functions_mapping

    functions_routes = check_usability_function(algorithm_type, functions_params, functions_mapping, task)
    if isinstance(functions_routes, Response):
        task.status = Task.Action.ERROR
        task.save()
        return functions_routes

    task.status = Task.Action.STARTED

    experiment_status = Experiment.Action.STARTED
    set_experiment_status(task, experiment_status)

    # wrapper_run_task(additional_params, task_config, functions_routes, task_id)
    celery_task_id = wrapper_run_task.delay(additional_params, task_config, functions_routes)
    task.celery_task_id = celery_task_id
    task.save()
    return success_response(f"Task {task.id} started successfully")
