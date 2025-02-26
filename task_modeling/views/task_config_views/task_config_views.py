from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, status
from rest_framework.response import Response

from api.utils.responses import not_found_response, permission_denied_response, bad_request_response, conflict_response, \
    created_response
from api.utils.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES
from task_modeling.models import TaskConfig
from task_modeling.serializers import TaskSerializer, TaskConfigSerializer
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin


class TaskConfigView(generics.ListCreateAPIView, PrepareTaskConfigMixin):
    serializer_class = TaskConfigSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = TaskConfig.objects.select_related("user").filter(user=user)
        return queryset

    @extend_schema(
        tags=["Task Configs"],
        summary="Get list of task configs",
        description="Get list of task configs",
        responses={
            status.HTTP_200_OK: TaskSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Task Configs'],
        summary="Create new task config",
        examples=[
            OpenApiExample(
                name='Example of an task config create request',
                value={
                    "name": "Task name",
                    "config": {
                        "example_param_1": "example_value",
                        "example_param_2": "example_value"
                    },
                    "user": "1",
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

        config_name = request.data.get("name", None)
        config = request.data.get("config", {})
        user_id = request.data.get("user", None)

        user = get_object_or_404(User, id=user_id)
        configs = [{"name": config_name, "config": config}]

        error_task_configs, existing_configs, created_configs = self.get_or_create_task_config(configs, user)
        if error_task_configs:
            return bad_request_response(created_configs)
        if existing_configs:
            existing_config = existing_configs[0]
            config_id = existing_config.id
            return conflict_response(config_id)

        created_config = created_configs[0]
        created_config_id = created_config.id

        return created_response(created_config_id)


class TaskConfigManagementView(generics.RetrieveAPIView):
    serializer_class = TaskConfigSerializer

    def get_object(self):
        task_config_id = self.kwargs.get("task_config_id")
        task_config_obj = TaskConfig.objects.select_related(
            "user"
        ).filter(id=task_config_id).first()
        if not task_config_obj:
            return not_found_response(f"{task_config_obj = }")

        user = self.request.user

        task_config_by_user = task_config_obj.user

        if user != task_config_by_user:
            return permission_denied_response()

        return task_config_obj

    @extend_schema(
        tags=["Task Configs"],
        summary="Get list of task configs",
        description="Get list of task configs",
        responses={
            status.HTTP_200_OK: TaskSerializer,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
