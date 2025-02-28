from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, status
from rest_framework.response import Response

from api.responses import not_found_response, permission_denied_response, bad_request_response, conflict_response, \
    created_response, success_response, no_content_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, STATUS_405, STATUS_204
from task_modeling.models import TaskConfig, Task
from task_modeling.serializers import TaskSerializer, TaskConfigSerializer
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin


class TaskConfigView(generics.ListCreateAPIView, PrepareTaskConfigMixin):
    serializer_class = TaskConfigSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()
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
        task_config_obj = self.get_queryset()
        if isinstance(task_config_obj, Response):
            return task_config_obj
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
        # user_id = request.data.get("user", None)
        # user = get_object_or_404(User, id=user_id)
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()

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


class TaskConfigManagementView(generics.RetrieveUpdateDestroyAPIView):
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
        task_obj = self.get_object()
        if isinstance(task_obj, Response):
            return task_obj
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Task Configs'],
        summary="Update task config",
        examples=[
            OpenApiExample(
                name='Example of an task config update request',
                value={
                    "name": "Task name",
                    "config": {
                        "algorithm": "master_worker",
                        "generations": 100,
                        "mutation_rate": 0.05,
                        "crossover_rate": 0.9,
                        "population_size": 200,
                        "fitness_function": "rastrigin"
                    }
                },
                request_only=True
            ),
        ],
        responses={
            **STATUS_405
        }
    )
    def put(self, request, *args, **kwargs):
        task_config = self.get_object()
        if isinstance(task_config, Response):
            return task_config

        task_config_id = task_config.id
        task_obj = Task.objects.select_related(
            "config", "experiment"
        ).filter(config_id=task_config_id, status=Task.Action.STARTED)
        if task_obj:
            return bad_request_response("Существуют запущенные задачи с этой конфигурацией")

        task_name = request.data.get("name", None)

        user = self.request.user
        config = request.data.get("config", {})
        error_config = PrepareTaskConfigMixin.validate_task_config(config, task_name, config,
                                                                   partial_check=False)
        if error_config or error_config == {}:
            return bad_request_response("Ошибка валидации конфигурации")

        config = PrepareTaskConfigMixin.order_params_task_config(config)
        task_config_obj = TaskConfig.objects.filter(config=config, user=user).first()
        if task_config_obj:
            return bad_request_response("Конфигурация задачи уже существует")


        task_config.name = task_name
        task_config.config = config
        task_config.save()
        return success_response(task_config.id)

    @extend_schema(
        tags=['Task Configs'],
        summary="Partial update experiment",
        examples=[
            OpenApiExample(
                name='Example of an experiment partial update request',
                value={
                    "name": "Task name",
                    "config": {
                        "algorithm": "master_worker",
                        "generations": 100,
                        "mutation_rate": 0.05,
                        "crossover_rate": 0.9,
                        "population_size": 200,
                        "fitness_function": "rastrigin"
                    }
                },
                request_only=True
            ),
        ],
        responses={
            status.HTTP_201_CREATED: TaskConfigSerializer,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def patch(self, request, *args, **kwargs):
        task_config = self.get_object()
        if isinstance(task_config, Response):
            return task_config

        task_config_id = task_config.id
        task_obj = Task.objects.select_related(
            "config", "experiment"
        ).filter(config_id=task_config_id, status=Task.Action.STARTED)
        if task_obj:
            return bad_request_response("Существуют запущенные задачи с этой конфигурацией")

        task_name = request.data.get("name", None)
        if task_name:
            task_config.name = task_name
        user = self.request.user
        config = request.data.get("config", {})
        if config:
            error_config = PrepareTaskConfigMixin.validate_task_config(config, None, config,
                                                                       partial_check=True)
            if error_config or error_config == {}:
                return bad_request_response("Ошибка валидации конфигурации")

            config = PrepareTaskConfigMixin.order_params_task_config(config)
            task_config_obj = TaskConfig.objects.filter(config=config, user=user).first()
            if task_config_obj:
                return bad_request_response("Конфигурация задачи уже существует")
            task_config.config = config
        task_config.save()
        return success_response(task_config.id)

    @extend_schema(
        tags=['Task Configs'],
        summary="Delete experiment",
        responses={
            **STATUS_204,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED,
        }
    )
    def delete(self, request, *args, **kwargs):
        task_config = self.get_object()
        if isinstance(task_config, Response):
            return task_config

        task_config_id = task_config.id
        task_obj = Task.objects.select_related(
            "config", "experiment"
        ).filter(config_id=task_config_id, status=Task.Action.STARTED)
        if task_obj:
            return bad_request_response("Существуют запущенные задачи с этой конфигурацией")

        task_config.delete()
        return no_content_response(task_config_id)
