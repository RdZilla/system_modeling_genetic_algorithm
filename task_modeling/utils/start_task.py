from api.utils.custom_logger import ExperimentLogger
from api.utils.load_custom_funcs.core_function_utils import CROSSOVER_FUNCTION_MAPPING
from core.models.master_worker_model import MasterWorkerGA
from task_modeling.models import Task


def run_task(task: Task) -> dict:
    response = {}

    experiment_name = task.experiment.name
    user_id = task.experiment.user_id
    task_id = task.id

    logger = ExperimentLogger(experiment_name, user_id, task_id)

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


    fitness_function = CROSSOVER_FUNCTION_MAPPING.get(fitness_function, None)
    if not fitness_function:
        task.status = Task.Action.ERROR
        task.save()
        response["delail"] = "Invalid fitness function"
        return response

    match algorithm_type:
        case "master_worker":
            ga = MasterWorkerGA(  # TODO проверить нужно ли передавать сюда количество генераций
                population_size=population_size,
                mutation_rate=mutation_rate,
                crossover_rate=crossover_rate,
                fitness_function=fitness_function,
                logger=logger
            )
            # TODO проверить нужно ли передавать сюда количество генераций
            # TODO по идее да, нам нужно останавливать расчёт, если количество генераций > чем заявлено в параметре generations
        case _:
            task.status = Task.Action.ERROR
            task.save()
            response["detail"] = "Invalid algorithm type"
            return response

    logger.logger_log.info(f"Task {task.id} started with config: {task_config}")
    # try:
    #     ga.run(generations)
    # except Exception as e:
    #     logger.logger_log.error(f"Task {task.id} failed with error: {e}")
    #     response["error"] = str(e)
    #     return response

    task.status = Task.Action.STARTED
    task.save()
    ga.run(generations)

    task.status = Task.Action.FINISHED
    task.save()
    response["message"] = f"Task {task.id} started successfully"
    return response