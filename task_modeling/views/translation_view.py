from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED


class TranslationView(generics.GenericAPIView):
    @extend_schema(
        tags=["API"],
        summary="Get list of translations for attrs",
        description="Get list of translations for attrs",
        responses={
            status.HTTP_200_OK: dict(),
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        translations = {
            "created": 'Создан',
            "updated": 'Обновлён',
            "started": 'Запущен',
            "finished": 'Завершён',
            "stopped": 'Остановлен',
            "error": 'Ошибка',
            "master_worker": 'Мастер воркер модель',
            "island_model": 'Островная модель',
            "asynchronous_model": 'Асинхронная модель',
            "algorithm": 'Алгоритм',
            "num_islands": 'Количество островов',
            "num_workers": 'Количество рабочих процессов',
            "mutation_rate": 'Вероятность мутации',
            "crossover_rate": 'Вероятность кроссинговера',
            "fitness_kwargs": 'Параметры функции приспособленности',
            "selection_rate": 'Вероятность отбора особей',
            "migration_rate": 'Частота миграции',
            "max_generations": 'Максимальное количество поколений',
            "mutation_kwargs": 'Параметры мутации',
            "population_size": 'Размер популяции',
            "crossover_kwargs": 'Параметры кроссинговера',
            "fitness_function": 'Функция приспособленности',
            "selection_kwargs": 'Параметры селекции',
            "mutation_function": 'Функция мутации',
            "crossover_function": 'Функция кроссинговера',
            "migration_interval": 'Интервал миграции',
            "selection_function": 'Функция селекции',
            "termination_kwargs": 'Параметры завершения',
            "termination_function": 'Функция завершения',
            "initialize_population_kwargs": 'Параметры инициализации популяции',
            "initialize_population_function": 'Функция инициализации популяции',
            "adaptation_function": 'Функция адаптации',
            "adaptation_kwargs": 'Параметры адаптации',
        }
        return Response(translations, status=status.HTTP_200_OK)
