from task_modeling.models import Experiment, Task


def set_experiment_status(task_obj, experiment_status):
    experiment_obj = task_obj.experiment

    related_tasks = Task.objects.filter(
        experiment=experiment_obj,
    )
    stopped_related_tasks = related_tasks.filter(status=Task.Action.STOPPED)
    running_related_tasks = related_tasks.filter(status=Task.Action.STARTED)
    error_related_tasks = related_tasks.filter(status=Task.Action.ERROR)
    if stopped_related_tasks:
        experiment_status = Experiment.Action.STOPPED
    if running_related_tasks:
        experiment_status = Experiment.Action.STARTED
    if error_related_tasks:
        experiment_status = Experiment.Action.ERROR
    experiment_obj.status = experiment_status
    experiment_obj.save()