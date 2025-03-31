from django.core.exceptions import ValidationError
from rest_framework import serializers

from task_modeling.models import Task, Experiment, TaskConfig


class ExperimentSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Experiment
        fields = "__all__"

    @staticmethod
    def get_tasks(instance):
        tasks = Task.objects.select_related(
            "config", "experiment"
        ).filter(experiment_id=instance.id)
        serializer_data = TaskSerializer(tasks, many=True).data
        return serializer_data


class TaskSerializer(serializers.ModelSerializer):
    config = serializers.SerializerMethodField()
    experiment_id = serializers.IntegerField(source="experiment.id")

    class Meta:
        model = Task
        fields = "__all__"

    @staticmethod
    def get_config(instance):
        config = instance.config
        config_data = TaskConfigSerializer(config).data
        return config_data


class TaskConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfig
        fields = "__all__"


def validate_file_extension(value):
    if not value.name.endswith('.py'):
        raise ValidationError("Только файлы с расширением .py разрешены.")
    return value


class MathFunctionsSerializer(serializers.Serializer):
    function_file = serializers.FileField(validators=[validate_file_extension])
