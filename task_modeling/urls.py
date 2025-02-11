from django.urls import path

from task_modeling.views import TaskView

urlpatterns = [
    path("tasks/", TaskView.as_view(), name="list_tasks_create_task"),
]