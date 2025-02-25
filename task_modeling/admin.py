from django.contrib import admin

from task_modeling.models import Task, TaskConfig, Experiment
from task_modeling.views import TaskManagementView


@admin.action(description="Запустить выбранные эксперименты")
def run_experiment_admin(modeladmin, request, queryset):
    return

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_select_related = ("user",)

    list_display = ("id", "name", "created_at", "user")
    search_fields = ("name",)
    list_filter = ("status",)
    list_per_page = 10
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "status")

    actions = [run_experiment_admin]


@admin.action(description="Запустить выбранную задачу")
def run_task_admin(modeladmin, request, queryset):
    list_response = []
    for task in queryset:
        response = TaskManagementView.run(task)
        list_response.append(response)
    return list_response

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_select_related = ("experiment", "config")

    list_display = ("id", "status", "config_id", "experiment", "created_at")
    list_filter = ("status", "experiment", "config_id")
    list_per_page = 10
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "status")

    actions = [run_task_admin]


@admin.register(TaskConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_select_related = ("user",)
    list_display = ("id", "name", "user", "created_at")
    list_filter = ("user",)
    list_per_page = 10
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
