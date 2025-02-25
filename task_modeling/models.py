from django.contrib.auth.models import User
from django.db import models


class Experiment(models.Model):
    class Action:
        CREATE = "create"
        UPDATE = "update"
        DELETE = "delete"
        STARTED = "started"
        FINISHED = "finished"
        STOPPED = "stopped"
        ERROR = "error"

        CHOICES_STATUSES = (
            (CREATE, "Создан"),
            (UPDATE, "Обновлен"),
            (DELETE, "Удалён"),

            (STARTED, "Запущен"),
            (FINISHED, "Завершен"),
            (STOPPED, "Остановлен"),
            (ERROR, "Ошибка"),
        )

    name = models.CharField(max_length=255, verbose_name="Название эксперимента")
    status = models.CharField(max_length=255, choices=Action.CHOICES_STATUSES, default=Action.CREATE,
                              verbose_name="Статус эксперимента")
    results_folder = models.CharField(max_length=255, verbose_name="Папка результатов", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания",
                                      help_text="Время создания эксперимента")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления",
                                      help_text="Время обновления данных эксперимента")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Пользователь", blank=True, null=True,
                             help_text="Пользователь, запустивший эксперимент")

    def __str__(self):
        return f"{self.name} with status {self.status}"

    class Meta:
        verbose_name = "Эксперимент"
        verbose_name_plural = "Эксперименты"


class TaskConfig(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название конфигурации")
    config = models.JSONField(default=dict, verbose_name="Конфигурация задачи")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания",
                                      help_text="Время создания конфигурации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления",
                                      help_text="Время обновления данных конфигурации")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Пользователь", blank=True, null=True,
                             help_text="Пользователь, создавший конфигурацию")

    def __str__(self):
        return f"Config id: {self.id} by {self.user.username}"

    class Meta:
        verbose_name = "Конфигурация задачи"
        verbose_name_plural = "Конфигурации задачи"


class Task(models.Model):
    class Action:
        CREATED = "created"
        STARTED = "started"
        FINISHED = "finished"
        STOPPED = "stopped"
        ERROR = "error"

        CHOICES_STATUSES = (
            (CREATED, "Создана"),
            (STARTED, "Запущена"),
            (FINISHED, "Завершена"),
            (STOPPED, "Остановлена"),
            (ERROR, "Ошибка"),
        )

    status = models.CharField(max_length=255, choices=Action.CHOICES_STATUSES, verbose_name="Статус задачи",
                              default=Action.CREATED)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания",
                                      help_text="Время создания задачи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления",
                                      help_text="Время обновления данных задачи")

    config = models.ForeignKey(TaskConfig, on_delete=models.SET_NULL, null=True, verbose_name="Конфигурация задачи")
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, verbose_name="Связь с экспериментом",
                                   help_text="В рамках какого эксперимента создана задача")

    def __str__(self):
        return f"{self.id} with config id: {self.config_id}"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
