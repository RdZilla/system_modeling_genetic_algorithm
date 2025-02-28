from django.urls import path

from task_modeling.views.experiment_views.experiment_views import ExperimentView, ExperimentManagementView
from task_modeling.views.task_config_views.task_config_views import TaskConfigView, TaskConfigManagementView
from task_modeling.views.task_functions.task_functions_view import MathFunctionsView
from task_modeling.views.task_views.task_views import TaskView, TaskManagementView

urlpatterns = [
    path("experiment", ExperimentView.as_view(), name="list_experiments_create_experiment"),
    path("experiment/<str:experiment_id>", ExperimentManagementView.as_view(), name="experiment_management"),
    path("experiment/<str:experiment_id>/tasks", TaskView.as_view(), name="list_tasks_create_task"),
    path("experiment/<str:experiment_id>/tasks/<str:task_id>", TaskManagementView.as_view(), name="task_management"),

    path("task_config", TaskConfigView.as_view(), name="list_configs_create_config"),
    path("task_config/<str:task_config_id>", TaskConfigManagementView.as_view(), name="task_config_management"),

    path("math_function", MathFunctionsView.as_view(), name="get_available_functions_create_function")
]