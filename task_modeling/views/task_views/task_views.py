import os
import shutil

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from api.responses import not_found_response, permission_denied_response, bad_request_response, no_content_response, \
    success_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, \
    SCHEMA_PERMISSION_DENIED, STATUS_204
from api.utils.custom_logger import get_user_folder_name, get_task_folder_name
from modeling_system_backend.settings import RESULT_ROOT

from task_modeling.models import Task
from task_modeling.serializers import TaskSerializer
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.utils.start_task import run_task


class TaskView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()

        experiment_id = self.kwargs.get("experiment_id")

        queryset = Task.objects.select_related(
            "config", "experiment"
        ).filter(
            experiment_id=experiment_id,
            experiment__user=user
        )
        return queryset


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
        task_obj = self.get_queryset()
        if isinstance(task_obj, Response):
            return task_obj
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Tasks'],
        summary="Create new task",
        examples=[
            OpenApiExample(
                name='Example of an task create request',
                value={
                    "config_id": "123",
                    "experiment_id": "1"
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
    def post(self, request, *args, **kwargs):  # TODO: доделать
        return super().post(request, *args, **kwargs)


class TaskManagementView(generics.RetrieveAPIView, generics.DestroyAPIView, PrepareTaskConfigMixin):
    serializer_class = TaskSerializer

    def get_object(self):
        user = self.request.user
        user_id = user.id
        if not user_id:
            return permission_denied_response()

        experiment_id = self.kwargs.get("experiment_id")

        task_id = self.kwargs.get("task_id")
        task_obj = Task.objects.select_related(
            "config", "experiment"
        ).filter(
            experiment_id=experiment_id,
            experiment__user=user,
            id=task_id
        ).first()
        if not task_obj:
            return not_found_response(f"{experiment_id = } {task_id = }")

        user = self.request.user

        experiment_by_user = task_obj.experiment.user

        if user != experiment_by_user:
            return permission_denied_response()

        return task_obj
    #
    @extend_schema(
        tags=['Tasks'],
        summary="Get / Start task by id",
        parameters=[
            OpenApiParameter(
                name="start", description='The parameter for starting the calculations of the task',
                type=bool, enum=[True, False], required=False
            ),
        ],
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

        is_start = request.query_params.get("start", "False")
        if is_start.lower() == "true":
            return self.start_task(task)
        return super().get(request, *args, **kwargs)

    @staticmethod
    def start_task(task: Task):
        # task_status = task.status
        # if task_status == Task.Action.STARTED:
        #     return bad_request_response("Задача уже запушена")
        # if task_status == Task.Action.FINISHED:
        #     return bad_request_response("Задача уже завершена. Перезапись резульатов запрещена")

        response = run_task(task)
        if status.is_client_error(response.status_code):
            return response
        return success_response(task.id)

    @extend_schema(
        tags=['Tasks'],
        summary="Delete task",
        responses={
            **STATUS_204,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED,
        }
    )
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        user = self.request.user
        if isinstance(task, Response):
            return task

        if task.status == Task.Action.STARTED:
            return bad_request_response("Active")

        user_id = user.id
        user_folder_name = get_user_folder_name(user_id)

        experiment_name = task.experiment.name

        task_id = task.id
        task_folder_name = get_task_folder_name(task_id)

        shutil.rmtree(os.path.join(RESULT_ROOT, user_folder_name, experiment_name, task_folder_name), ignore_errors=True)

        task.delete()
        return no_content_response(task_id)
