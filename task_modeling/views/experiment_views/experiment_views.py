import os
import shutil

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from api.responses import bad_request_response, created_response, not_found_response, permission_denied_response, \
    no_content_response, success_response, method_not_allowed_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, STATUS_204, STATUS_405
from api.utils.custom_logger import get_user_folder_name
from modeling_system_backend.settings import RESULT_ROOT
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.models import Experiment, Task
from task_modeling.serializers import ExperimentSerializer
from task_modeling.utils.start_task import run_task


class ExperimentView(generics.ListCreateAPIView, PrepareTaskConfigMixin):
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()
        queryset = Experiment.objects.select_related(
            "user"
        ).filter(
            user=user
        )
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
        experiment_obj = self.get_queryset()
        if isinstance(experiment_obj, Response):
            return experiment_obj
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Experiments'],
        summary="Create new experiment",
        examples=[
            OpenApiExample(
                name='Example of an experiment create request',
                value={
                    "name": "Task name",
                    "configs": [
                        {
                            "name": "test_task_config",
                            "config": {
                                "algorithm": "master_worker",
                                "population_size": 200,
                                "chrom_length": 10,
                                "max_generations": 100,
                                "mutation_rate": 0.05,
                                "crossover_rate": 0.05,
                                "selection_rate": 0.9,
                                "num_workers": 3,
                                "crossover_function": "single_point_crossover",
                                "fitness_function": "rastrigin_fitness",
                                "initialize_population_function": "random_initialization",
                                "mutation_function": "bitwise_mutation",
                                "selection_function": "tournament_selection",
                                "termination_function": "generation_limit_termination"
                            }
                        },
                        {
                            "name": "test_task_config",
                            "config": {
                                "algorithm": "master_worker",
                                "population_size": 200,
                                "chrom_length": 10,
                                "max_generations": 100,
                                "mutation_rate": 0.05,
                                "crossover_rate": 0.05,
                                "selection_rate": 0.9,
                                "num_workers": 3,
                                "crossover_function": "single_point_crossover",
                                "fitness_function": "rastrigin_fitness",
                                "initialize_population_function": "random_initialization",
                                "mutation_function": "bitwise_mutation",
                                "selection_function": "tournament_selection",
                                "termination_function": "generation_limit_termination"
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

        validate_response = self.validate_experiment_data(experiment_name)
        if isinstance(validate_response, Response):
            return validate_response

        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()

        error_task_configs, existing_configs, created_configs = self.get_or_create_task_config(configs, user)
        if error_task_configs:
            return bad_request_response(created_configs)

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
    ) -> (Response | None):
        """
        Validation of input parameters when creating an experiment.\n
        if the function returns None, it means that the validation was successful.\n
        if the function returns any kind of Response, it means that the validation passed with errors.
        :param experiment_name: name of the future experiments
        :return: Error response
        """
        if not experiment_name:
            error_text = "Название эксперимента должно быть заполнено"
            return bad_request_response(error_text)
        exist_experiment = Experiment.objects.filter(name=experiment_name)
        if exist_experiment:
            return bad_request_response(f"Experiment with name={experiment_name} already exist")


class ExperimentManagementView(generics.RetrieveUpdateDestroyAPIView):
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

        return super().get(request, *args, **kwargs)

    @staticmethod
    def start_experiment(experiment):
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
            if response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]:
                error_list.append({task.id: response.data})
                continue
            response_list.append(response.data)

        if error_list:
            experiment.status = Experiment.Action.ERROR
            experiment.save()
            return bad_request_response(error_list)
        return success_response(response_list)

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
                    "name": "Task name",
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
