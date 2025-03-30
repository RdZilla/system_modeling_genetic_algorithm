import json
import os
import shutil

from django.http import FileResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from api.responses import not_found_response, permission_denied_response, bad_request_response, no_content_response, \
    success_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES, \
    SCHEMA_PERMISSION_DENIED, STATUS_204
from api.utils.custom_logger import get_user_folder_name, get_task_folder_name, JSON_LOG_FILE_NAME, RESULT_KEY, \
    BEST_PLOT_FILE_NAME, ALL_RESULTS_PLOT_FILE_NAME
from api.utils.export_results import plot_results
from modeling_system_backend.celery import app
from modeling_system_backend.settings import RESULT_ROOT

from task_modeling.models import Task
from task_modeling.serializers import TaskSerializer
from task_modeling.utils.prepare_task_config import PrepareTaskConfigMixin
from task_modeling.utils.start_task import run_task


class TaskMixin:
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


class TaskManagementView(TaskMixin,
                         generics.RetrieveAPIView,
                         generics.DestroyAPIView,
                         PrepareTaskConfigMixin):
    serializer_class = TaskSerializer

    @extend_schema(
        tags=['Tasks'],
        summary="Get / Start task by id",
        parameters=[
            OpenApiParameter(
                name="start", description='The parameter for starting the calculations of the task',
                type=bool, enum=[True, False], required=False
            ),
            OpenApiParameter(
                name="stop", description='The parameter for stopping the calculations of the task',
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

        is_stop = request.query_params.get("stop", "False")
        if is_stop.lower() == "true":
            return self.stop_task(task)

        return super().get(request, *args, **kwargs)

    @staticmethod
    def start_task(task: Task):
        # task_status = task.status
        # if task_status == Task.Action.STARTED:
        #     return bad_request_response("Задача уже запушена")
        # if task_status == Task.Action.FINISHED:
        #     return bad_request_response("Задача уже завершена. Перезапись результатов запрещена")

        response = run_task(task)
        if status.is_client_error(response.status_code):
            return response
        return success_response(task.id)

    @staticmethod
    def stop_task(task: Task):
        # task_status = task.status
        # if task_status == Task.Action.STOPPED:
        #     return bad_request_response("Задача уже остановлена")
        # if task_status == Task.Action.FINISHED:
        #     return bad_request_response("Задача уже завершена. Перезапись результатов запрещена")
        # if task_status == Task.Action.ERROR:
        #     return bad_request_response("Задача с ошибкой. Остановка невозможна")

        celery_task_id = task.celery_task_id
        if not celery_task_id:
            return bad_request_response("exist celery task id")

        app.control.revoke(celery_task_id, terminate=True)

        task.status = Task.Action.STOPPED
        task.save()

        return success_response("celery task has been cancelled")

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
        celery_task_id = task.celery_task_id
        if celery_task_id:
            app.control.revoke(celery_task_id, terminate=True)

        task_folder_name = get_task_folder_name(task_id)
        shutil.rmtree(os.path.join(RESULT_ROOT, user_folder_name, experiment_name, task_folder_name),
                      ignore_errors=True)

        task.delete()
        return no_content_response(task_id)


class ExportResult(TaskMixin, generics.GenericAPIView):
    @extend_schema(
        tags=['Tasks'],
        summary="Get results",
        parameters=[
            OpenApiParameter(
                name="final_result_png", description='The parameter for getting final result',
                type=bool, enum=[True, False], required=False
            ),
            OpenApiParameter(
                name="all_workers_png", description='The parameter for getting all results',
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

        user = self.request.user
        user_id = user.id
        user_folder_name = get_user_folder_name(user_id)
        experiment_name = task.experiment.name
        task_id = task.id
        task_folder_name = get_task_folder_name(task_id)
        result_path = os.path.join(RESULT_ROOT, user_folder_name, experiment_name, task_folder_name)

        final_result_png = request.query_params.get("final_result_png", "false")
        if final_result_png.lower() == "true":
            return self.get_final_result_png(result_path)

        all_workers = request.query_params.get("all_workers_png", "false")
        if all_workers.lower() == "true":
            return self.get_all_results(result_path)

    def get_final_result_png(self, result_path):
        json_path = os.path.join(result_path, JSON_LOG_FILE_NAME)
        with open(json_path, "r") as json_file:
            result_dict = json.load(json_file)
        plot_path = os.path.join(result_path, BEST_PLOT_FILE_NAME)
        not_valid = plot_results(result_dict, plot_path, only_result=True)
        if not_valid:
            return bad_request_response(not_valid)
        return self.get_picture(plot_path)

    def get_all_results(self, result_path):
        json_path = os.path.join(result_path, JSON_LOG_FILE_NAME)
        with open(json_path, "r") as json_file:
            result_dict = json.load(json_file)
        plot_path = os.path.join(result_path, ALL_RESULTS_PLOT_FILE_NAME)
        not_valid = plot_results(result_dict, plot_path)
        if not_valid:
            return bad_request_response(not_valid)
        return self.get_picture(plot_path)

    @staticmethod
    def get_picture(plot_path):
        with open(plot_path, 'rb'):
            response = FileResponse(open(plot_path, 'rb'), content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="file.png"'
        return response
