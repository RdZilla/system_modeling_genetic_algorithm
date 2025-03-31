import os
import shutil

from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.status import is_client_error

from api.responses import bad_request_response, created_response, not_found_response, permission_denied_response, \
    no_content_response, success_response, method_not_allowed_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, STATUS_204, STATUS_405
from api.utils.custom_logger import get_user_folder_name
from modeling_system_backend.celery import app
from modeling_system_backend.settings import RESULT_ROOT
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.models import Experiment, Task
from task_modeling.serializers import ExperimentSerializer
from task_modeling.utils.start_task import run_task

User = get_user_model()

search_vector = SearchVector(
    "name",
    "status",
    "task_status",
    "task_celery_task_id",
    "task_config_name",
)

FILTER_DICT = {
    "search": lambda filter_value: Q(search=SearchQuery(filter_value, search_type="websearch")),
    "experimentStatus[]": lambda filter_value: Q(status__in=filter_value),
    "taskStatus[]": lambda filter_value: Q(task__status__in=filter_value),
    "createdFrom": lambda filter_value: Q(created_at__gte=filter_value),
    "createdTo": lambda filter_value: Q(created_at__lte=filter_value),
    "updatedFrom": lambda filter_value: Q(updated_at__gte=filter_value),
    "updatedTo": lambda filter_value: Q(updated_at__lte=filter_value),
    "configIds[]": lambda filter_value: Q(task__config__id__in=filter_value),
}


class ExperimentMixin:
    @staticmethod
    def start_experiment(experiment: Experiment):
        tasks = Task.objects.select_related(
            "config", "experiment"
        ).filter(
            experiment=experiment,
            # status=Task.Action.CREATED
        )

        if not tasks:
            experiment_id = experiment.id
            return not_found_response(f"task with {experiment_id = }")

        # experiment.status = Experiment.Action.STARTED
        # experiment.save()

        response_list = []
        error_list = []

        for task in tasks:
            response = run_task(task)
            if status.is_client_error(response.status_code):
                error_list.append({task.id: response.data})
                continue
            response_list.append(response.data)

        if error_list:
            experiment.status = Experiment.Action.ERROR
            experiment.save()
            return bad_request_response(error_list)
        return success_response(response_list)

    @staticmethod
    def stop_experiment(experiment: Experiment):
        tasks = Task.objects.select_related(
            "config", "experiment"
        ).filter(
            experiment=experiment,
            # status=Task.Action.CREATED
        )

        if not tasks:
            experiment_id = experiment.id
            return not_found_response(f"task with {experiment_id = }")

        response_list = []
        error_list = []

        for task in tasks:
            celery_task_id = task.celery_task_id
            if not celery_task_id:
                error_list.append({task.id: "exist celery task id"})
                continue

            app.control.revoke(celery_task_id, terminate=True)
            response_list.append({task.id: "celery task has been cancelled"})

            # task.status = Task.Action.STOPPED
            # task.save()
        if error_list:
            experiment.status = Experiment.Action.ERROR
            experiment.save()
            return bad_request_response(error_list)

        # experiment.status = Experiment.Action.STOPPED
        # experiment.save()
        return success_response(response_list)


class ExperimentView(generics.ListCreateAPIView, PrepareTaskConfigMixin):
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()
        queryset = Experiment.objects.prefetch_related(
            "task_set",
            "task_set__config"
        ).select_related(
            "user"
        ).filter(
            user=user
        ).annotate(
            task_status=StringAgg('task__status', delimiter=' '),
            task_celery_task_id=StringAgg('task__celery_task_id', delimiter=' '),
            task_config_name=StringAgg('task__config__name', delimiter=' '),
        ).annotate(
            search=search_vector
        ).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        list_params = ["experimentStatus[]", "taskStatus[]", "configIds[]"]
        filter_params = self.request.query_params.lists()

        full_filter = Q()
        for filters in filter_params:
            filter_name = filters[0]
            filter_value = filters[1]
            if filter_name not in FILTER_DICT:
                continue
            if filter_name not in list_params:
                filter_value = filter_value[0]
            if not filter_value or (isinstance(filter_value, list) and not filter_value[0]):
                continue

            filter_q = FILTER_DICT[filter_name](filter_value)
            full_filter &= filter_q
        queryset = queryset.filter(full_filter)
        return queryset

    @extend_schema(
        tags=["Experiments"],
        summary="Get list of experiments",
        description="Get list of experiments by user_id",
        responses={
            status.HTTP_200_OK: ExperimentSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        experiment_qs = self.get_queryset()
        if isinstance(experiment_qs, Response):
            return experiment_qs
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Experiments'],
        summary="Create new experiment",
        examples=[
            OpenApiExample(
                name='Example of an experiment create request',
                value={
                    "name": "Experiment name",
                    "configs": [
                        {
                            "name": "master_worker_config_1",
                            "config": {
                                "algorithm": "master_worker",
                                "population_size": 100,
                                "max_generations": 50,
                                "mutation_rate": 0.05,
                                "crossover_rate": 0.75,
                                "num_workers": 3,
                                "crossover_function": "single_point_crossover",
                                "crossover_kwargs": {},
                                "fitness_function": "rastrigin_fitness",
                                "fitness_kwargs": {},
                                "initialize_population_function": "random_init",
                                "initialize_population_kwargs": {
                                    "chrom_length": 10,
                                },
                                "mutation_function": "bitwise_mutation",
                                "mutation_kwargs": {},
                                "selection_function": "tournament_selection",
                                "selection_kwargs": {
                                    "tournament_size": 3,
                                    "min_max_rule": "min",
                                },
                            }
                        },
                        {
                            "name": "island_model_config_1",
                            "config": {
                                "algorithm": "island_model",
                                "population_size": 100,
                                "max_generations": 50,
                                "mutation_rate": 0.05,
                                "crossover_rate": 0.75,
                                "num_workers": 3,
                                "crossover_function": "single_point_crossover",
                                "crossover_kwargs": {},
                                "fitness_function": "rastrigin_fitness",
                                "fitness_kwargs": {},
                                "initialize_population_function": "random_init",
                                "initialize_population_kwargs": {
                                    "chrom_length": 10,
                                },
                                "mutation_function": "bitwise_mutation",
                                "mutation_kwargs": {},
                                "selection_function": "tournament_selection",
                                "selection_kwargs": {
                                    "tournament_size": 3,
                                    "min_max_rule": "min",
                                },
                                "num_islands": 3,
                                "migration_interval": 5,
                                "migration_rate": 0.5
                            }
                        },
                    ]
                },
                request_only=True
            ),
        ],
        responses={
            status.HTTP_201_CREATED: ExperimentSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def post(self, request, *args, **kwargs):
        experiment_name = request.data.get("name", None)
        configs = request.data.get("configs", [])

        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()

        validate_response = self.validate_experiment_data(experiment_name, user)
        if isinstance(validate_response, Response):
            return validate_response

        error_task_configs, existing_configs, created_configs = self.get_or_create_task_config(configs, user)
        if error_task_configs:
            error_config = ';\n'.join(created_configs)
            error_message = f"Ошибки создания конфигурации: {error_config}"
            return bad_request_response(error_message)

        experiment_obj = Experiment.objects.create(
            name=experiment_name,
            user=user
        )

        configs = existing_configs + created_configs
        for config in configs:
            Task.objects.create(
                config=config,
                experiment=experiment_obj
            )
        return created_response(experiment_obj.id)

    @staticmethod
    def validate_experiment_data(
            experiment_name: (str | None),
            user: User,
    ) -> (Response | None):
        """
        Validation of input parameters when creating an experiment.\n
        if the function returns None, it means that the validation was successful.\n
        if the function returns any kind of Response, it means that the validation passed with errors.
        :param experiment_name: name of the future experiments
        :param user: user object
        :return: Error response
        """
        if not experiment_name:
            error_text = "Название эксперимента должно быть заполнено"
            return bad_request_response(error_text)

        exist_experiment = Experiment.objects.filter(name=experiment_name, user=user)
        if exist_experiment:
            return bad_request_response(f"Experiment with name='{experiment_name}' already exist")


class ExperimentManagementView(ExperimentMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperimentSerializer

    def get_object(self):
        experiment_id = self.kwargs.get("experiment_id")
        experiment_obj = Experiment.objects.select_related(
            "user"
        ).filter(
            id=experiment_id
        ).first()
        if not experiment_obj:
            return not_found_response(f"{experiment_id = }")

        user_id = self.request.user
        experiment_by_user = experiment_obj.user
        if user_id != experiment_by_user:
            return permission_denied_response()

        return experiment_obj

    @extend_schema(
        tags=['Experiments'],
        summary="Get experiment by id",
        parameters=[
            OpenApiParameter(
                name="start", description='The parameter for starting the calculations of the experiment',
                type=bool, enum=[True, False], required=False
            ),
            OpenApiParameter(
                name="stop", description='The parameter for stopping the calculations of the experiment',
                type=bool, enum=[True, False], required=False
            ),
        ],
        responses={
            status.HTTP_200_OK: ExperimentSerializer,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        experiment = self.get_object()
        if isinstance(experiment, Response):
            return experiment

        is_start = request.query_params.get("start", "False").lower() == "true"
        if is_start:
            return self.start_experiment(experiment)

        is_stop = request.query_params.get("stop", "False").lower() == "true"
        if is_stop:
            return self.stop_experiment(experiment)

        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Experiments'],
        summary="Update experiment",
        description="METHOD NOT ALLOWED",
        examples=[
            OpenApiExample(
                name='METHOD NOT ALLOWED',
                value={"METHOD NOT ALLOWED"}
            )
        ],
        responses={
            **STATUS_405
        }
    )
    def put(self, request, *args, **kwargs):
        return method_not_allowed_response()

    @extend_schema(
        tags=['Experiments'],
        summary="Partial update experiment",
        examples=[
            OpenApiExample(
                name='Example of an experiment partial update request',
                value={
                    "name": "Experiment name",
                },
                request_only=True
            ),
        ],
        responses={
            status.HTTP_201_CREATED: ExperimentSerializer,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def patch(self, request, *args, **kwargs):
        experiment_obj = self.get_object()
        if isinstance(experiment_obj, Response):
            return experiment_obj

        new_experiment_name = request.data.get("name")
        if not new_experiment_name:
            return bad_request_response("New name must be filled in")
        exist_name = Experiment.objects.filter(name=new_experiment_name)
        if exist_name:
            return bad_request_response(f"Experiment with name={new_experiment_name} already exist")

        user = self.request.user
        user_id = user.id
        user_folder_name = get_user_folder_name(user_id)
        experiment_name = experiment_obj.name

        experiment_folder_old_name = os.path.join(RESULT_ROOT, user_folder_name, experiment_name)
        experiment_folder_new_name = os.path.join(RESULT_ROOT, user_folder_name, new_experiment_name)
        try:
            os.rename(experiment_folder_old_name, experiment_folder_new_name)
        except FileNotFoundError:
            os.makedirs(experiment_folder_new_name, exist_ok=True)

        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=['Experiments'],
        summary="Delete experiment",
        responses={
            **STATUS_204,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED,
        }
    )
    def delete(self, request, *args, **kwargs):
        experiment = self.get_object()
        user = self.request.user

        if isinstance(experiment, Response):
            return experiment

        experiment_id = experiment.id

        experiment_is_started = experiment.status == Experiment.Action.STARTED
        tasks_qs = Task.objects.select_related(
            "config", "experiment"
        ).filter(experiment=experiment)

        active_tasks = tasks_qs.filter(status=Task.Action.STARTED)
        if experiment_is_started or active_tasks:
            return bad_request_response("Active")

        user_id = user.id
        user_folder_name = get_user_folder_name(user_id)
        experiment_name = experiment.name
        shutil.rmtree(os.path.join(RESULT_ROOT, user_folder_name, experiment_name), ignore_errors=True)

        experiment.delete()
        tasks_qs.delete()
        return no_content_response(experiment_id)


class MultipleLaunchView(ExperimentMixin, generics.GenericAPIView):
    def get_queryset(self):
        experiment_ids = self.request.data.get("experiment_ids", [])
        # status_filter = Q(
        #     ~Q(status=Experiment.Action.STARTED) |
        #     ~Q(status=Experiment.Action.FINISHED) |
        #     ~Q(status=Experiment.Action.DELETED)
        # )
        qs = Experiment.objects.filter(id__in=experiment_ids)
        # qs = qs.filter(status_filter)
        return qs

    def post(self, request, *args, **kwargs):
        response_list = []

        qs = self.get_queryset()
        for experiment in qs:
            experiment_id = experiment.id
            experiment_name = experiment.name

            response = self.start_experiment(experiment)
            status_code = response.status_code
            if is_client_error(status_code):
                response_list.append(f"[{experiment_id}|{experiment_name}] - Ошибка запуска")
                continue
            response_list.append(f"[{experiment_id}|{experiment_name}] - успешно запущен")

        return success_response(response_list)
