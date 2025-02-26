from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from api.utils.responses import bad_request_response, created_response, not_found_response, permission_denied_response
from api.utils.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.models import Experiment, Task
from task_modeling.serializers import ExperimentSerializer


class ExperimentView(generics.ListCreateAPIView, PrepareTaskConfigMixin):
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        user = self.request.user
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
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Experiments'],
        summary="Create new experiment",
        examples=[
            OpenApiExample(
                name='Example of an experiment create request',
                value={
                    "name": "Task name",
                    "user": "user_id",
                    "configs": [
                        {
                            "name": "config_name",
                            "config": {
                                "example_param_1": "example_value",
                                "example_param_2": "example_value"
                            }
                        },
                        {
                            "name": "config_name",
                            "config": {
                                "example_param_1": "example_value",
                                "example_param_2": "example_value"
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
        experiment_user_id = request.data.get("user", None)
        configs = request.data.get("configs", [])

        user = self.validate_experiment_data(experiment_name, experiment_user_id)

        if isinstance(user, Response):
            return user

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
            experiment_user_id: (str | None),
    ) -> (Response | User):
        """
        Validation of input parameters when creating an experiment.\n
        if the function returns None, it means that the validation was successful.\n
        if the function returns any kind of Response, it means that the validation passed with errors.
        :param experiment_name: name of the future experiments
        :param experiment_user_id: the ID of the user who initiated the future experiments
        :return: Error response or User obj
        """
        if not experiment_name:
            error_text = "Название эксперимента должно быть заполнено"
            return bad_request_response(error_text)

        user = get_object_or_404(User, id=experiment_user_id)

        return user


class ExperimentManagementView(generics.RetrieveAPIView):
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

        is_start = request.query_params.get("start", "False")
        if is_start.lower() == "true":
            return Response({}, 501)   # TODO реализовать запуск
        return super().get(request, *args, **kwargs)
