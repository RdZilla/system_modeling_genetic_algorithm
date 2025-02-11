from django.contrib import admin

from task_modeling.models import Task, UserConfig


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at', 'status')
    search_fields = ('name', 'status')
    list_filter = ('status',)
    list_editable = ('status',)
    list_per_page = 10
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user',)
    list_filter = ('user',)
    list_per_page = 10
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
