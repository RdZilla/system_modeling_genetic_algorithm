from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, status

from api.utils.statuses import SCHEMA_GET_POST_STATUSES

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
            **SCHEMA_GET_POST_STATUSES
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
                },
                request_only=True
            ),
        ],
        responses={
            status.HTTP_201_CREATED: TaskSerializer,
            **SCHEMA_GET_POST_STATUSES
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
