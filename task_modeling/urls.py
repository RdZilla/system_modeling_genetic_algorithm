from django.urls import path

from task_modeling.views.experiment_views.experiment_views import ExperimentView, ExperimentManagementView, \
    MultipleLaunchView
from task_modeling.views.task_config_views.task_config_views import TaskConfigView, TaskConfigManagementView
from task_modeling.views.math_functions.math_functions_view import MathFunctionsView, GetSupportedAlgorithmView
from task_modeling.views.task_views.task_views import TaskView, TaskManagementView, ExportResult, StartedTaskView
from task_modeling.views.translation_view import TranslationView

urlpatterns = [
    path("experiment", ExperimentView.as_view(), name="list_experiments_create_experiment"),
    path("experiment/<str:experiment_id>", ExperimentManagementView.as_view(), name="experiment_management"),
    path("experiment/<str:experiment_id>/task", TaskView.as_view(), name="list_tasks_create_task"),
    path("experiment/<str:experiment_id>/task/<str:task_id>", TaskManagementView.as_view(), name="task_management"),
    path("experiment/<str:experiment_id>/task/<str:task_id>/export_result", ExportResult.as_view(), name="task_management"),

    path("started_task", StartedTaskView.as_view(), name="started_task"),

    path("task_config", TaskConfigView.as_view(), name="list_configs_create_config"),
    path("task_config/<str:task_config_id>", TaskConfigManagementView.as_view(), name="task_config_management"),

    path("math_function", MathFunctionsView.as_view(), name="get_available_functions_create_function"),
    path("get_supported_algorithms", GetSupportedAlgorithmView.as_view(), name="get_available_functions_create_function"),
    path("multiple_launch", MultipleLaunchView.as_view(), name="multiple_launch_experiments"),
    path("translations", TranslationView.as_view(), name="translations")
]
