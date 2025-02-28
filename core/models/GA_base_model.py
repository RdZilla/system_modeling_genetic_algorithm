import json
from abc import ABC, abstractmethod

from task_modeling.models import Task, Experiment


class GeneticAlgorithm(ABC):
    def __init__(self, population_size, mutation_rate, crossover_rate, fitness_function=None, logger=None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.fitness_function = fitness_function
        self.population = self.initialize_population()

        self.logger = logger

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)

    @abstractmethod
    def initialize_population(self):
        """Инициализация начальной популяции"""
        pass

    @abstractmethod
    def selection(self):
        """Выбор родителей"""
        pass

    @abstractmethod
    def crossover(self, parent1, parent2):
        """Скрещивание"""
        pass

    @abstractmethod
    def mutation(self, individual):
        """Мутация"""
        pass

    @abstractmethod
    def evaluate_fitness(self):
        """Оценка приспособленности"""
        pass

    @abstractmethod
    def run(self, task_id, generations, task_config):
        """Запуск алгоритма"""
        pass

    @staticmethod
    def finish(task_id):
        """Завершение алгоритма"""
        task_obj = Task.objects.get(id=task_id)
        task_obj.status = Task.Action.FINISHED
        task_obj.save()

        experiment_obj = task_obj.experiment

        experiment_status = Experiment.Action.FINISHED

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
