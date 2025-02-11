from django.contrib import admin

from task_modeling.models import Task, UserConfig
from task_modeling.views import TaskManagementView

@admin.action(description="Run task")
def run_task_admin(modeladmin, request, queryset):
    list_response = []
    for task in queryset:
        response = TaskManagementView.run(task)
        list_response.append(response)
    return list_response

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'config_id', 'created_at', 'updated_at', 'status')
    search_fields = ('name', 'status')
    list_filter = ('status', 'config_id')
    list_per_page = 10
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'status')

    actions = [run_task_admin]


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user',)
    list_filter = ('user',)
    list_per_page = 10
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
