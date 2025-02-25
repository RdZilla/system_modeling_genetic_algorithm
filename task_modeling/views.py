from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, status
from rest_framework.response import Response

from api.utils.custom_logger import ExperimentLogger
from api.utils.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, \
    SCHEMA_PERMISSION_DENIED
from core.fitness.rastrigin_fitness import rastrigin
from core.models.master_worker_model import MasterWorkerGA

from task_modeling.models import Task
from task_modeling.serializers import TaskSerializer


class TaskView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @extend_schema(
        tags=["Tasks"],
        summary="Get list of tasks",
        description="Get list of tasks",
        responses={
            status.HTTP_200_OK: TaskSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Tasks'],
        summary="Create new task",
        examples=[
            OpenApiExample(
                name='Example of an task create request',
                value={
                    "name": "Task name",
                    "status": "create",
                    "config": "123"
                },
                request_only=True
            ),
        ],
        responses={
            status.HTTP_201_CREATED: TaskSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaskManagementView(generics.RetrieveAPIView):
    serializer_class = TaskSerializer

    def get_object(self):
        task_id = self.kwargs.get("task_id")
        task_obj = Task.objects.select_related(
            "config", "experiment"
        ).filter(id=task_id).first()
        if not task_obj:
            return Response({"detail": "Object has not found"}, status=status.HTTP_404_NOT_FOUND)

        user_id = self.request.user

        experiment_by_user_id = task_obj.experiment.user_id

        if user_id != experiment_by_user_id:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        return task_obj
    #
    @extend_schema(
        tags=['Tasks'],
        summary="Start task by id",
        responses={
            status.HTTP_200_OK: TaskSerializer,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        task = self.get_object()
        if isinstance(task, Response):
            return task

        # validate_data = self.validate_data(task)
        # TODO add error response if validate is not sucsessfull
        # TODO create periodic task and 200 response

        response = self.run(task)

        response_status = status.HTTP_200_OK
        if "error" in response:
            response_status = status.HTTP_400_BAD_REQUEST
        return Response(response, status=response_status)

    @staticmethod
    def run(task: Task) -> dict:
        response = {}

        experiment_name = task.experiment.name
        user_id = task.experiment.user_id
        task_id = task.id

        logger = ExperimentLogger(experiment_name, user_id, task_id)

        task_config = task.config.config
        algorithm_type = task_config.get("algorithm")

        generations = task_config.get("generations")

        population_size = task_config.get("population_size")
        mutation_rate = task_config.get("mutation_rate")
        crossover_rate = task_config.get("crossover_rate")

        fitness_function = task_config.get("fitness_function")
        # selection_function = ...  TODO: add selection_function
        # crossover_function = ...  TODO: add crossover_function
        # mutation_function = ...   TODO: add mutation_function

        # TODO: Убрать из абстрактного класса абстракцию с методов на селекцию, кроссинговер и мутацию.
        #  Реализовать в абстрактном классе логики селекции, кроссинговера и мутацию и наследовать их в каждом алгоритме

        # TODO: Добавить валидацию данных

        match fitness_function:
            case "rastrigin":
                fitness_function = rastrigin
            case _:
                response["error"] = "Invalid fitness function"
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
                response["error"] = "Invalid algorithm type"
                return response

        logger.logger_log.info(f"Task {task.id} started with config: {task_config}")
        # try:
        #     ga.run(generations)
        # except Exception as e:
        #     logger.logger_log.error(f"Task {task.id} failed with error: {e}")
        #     response["error"] = str(e)
        #     return response

        ga.run(generations)

        response["message"] = f"Task {task.id} started successfully"
        return response
