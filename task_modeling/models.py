from django.contrib.auth.models import User
from django.db import models


class UserConfig(models.Model):
    name = models.CharField(max_length=255, verbose_name='Config name', blank=True)
    config = models.JSONField(default=dict, verbose_name='Config')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')

    def __str__(self):
        return f"Config id: {self.id} by {self.user.username}"

    class Meta:
        verbose_name = 'User Config'
        verbose_name_plural = 'User Configs'



class Task(models.Model):
    class Action:
        CREATE = 'create'
        UPDATE = 'update'
        DELETE = 'delete'

        STARTED = 'started'
        FINISHED = 'finished'
        STOPPED = 'stopped'
        ERROR = 'error'


        CHOICES_STATUSES = (
            (CREATE, 'Create'),
            (UPDATE, 'Update'),
            (DELETE, 'Delete'),

            (STARTED, 'Started'),
            (FINISHED, 'Finished'),
            (STOPPED, 'Stopped'),
            (ERROR, 'Error'),
        )

    name = models.CharField(max_length=255, verbose_name='Task name')
    task_folder = models.CharField(max_length=255, verbose_name='Task folder', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    status = models.CharField(max_length=255, choices=Action.CHOICES_STATUSES, default=Action.CREATE,
                              verbose_name='Status')

    config = models.ForeignKey(UserConfig, on_delete=models.SET_NULL, null=True, verbose_name='Config')
    task_model = models.CharField(max_length=255, verbose_name='Task model', blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', blank=True, null=True)

    def __str__(self):
        return f"{self.name} with config id: {self.config_id}"

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'