from django.urls import path

from task_modeling.views import TaskView, TaskManagementView

urlpatterns = [
    path("tasks/", TaskView.as_view(), name="list_tasks_create_task"),
    path("tasks/<str:pk>", TaskManagementView.as_view(), name="task_management"),
]