from django.contrib.auth.models import User
from django.db import models


class UserConfig(models.Model):
    config = models.JSONField(default=dict, verbose_name='Config')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')

    def __str__(self):
        return f"Config for {self.user.username}"

    class Meta:
        verbose_name = 'User Config'
        verbose_name_plural = 'User Configs'



class Task(models.Model):
    class Action:
        CREATE = 'create'
        UPDATE = 'update'
        DELETE = 'delete'

        CHOICES_STATUSES = (
            (CREATE, 'Create'),
            (UPDATE, 'Update'),
            (DELETE, 'Delete'),
        )

    name = models.CharField(max_length=255, verbose_name='Task name')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    status = models.CharField(max_length=255, choices=Action.CHOICES_STATUSES, default=Action.CREATE,
                              verbose_name='Status')
    config = models.ForeignKey(UserConfig, on_delete=models.SET_NULL, null=True, verbose_name='Config')

    def __str__(self):
        return f"{self.name} with config id: {self.config_id}"

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'