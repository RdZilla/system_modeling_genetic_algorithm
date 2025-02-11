from django.db import models

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

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=Action.CHOICES_STATUSES, default=Action.CREATE)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
