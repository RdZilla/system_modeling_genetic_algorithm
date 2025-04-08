from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED
from api.utils.load_custom_funcs.UserFunctionMixin import UserFunctionMixin
from api.utils.load_custom_funcs.load_custom_functions import get_translations_from_function


class TranslationView(generics.GenericAPIView, UserFunctionMixin):
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
        statuses = {
            "created": 'Создан',
            "updated": 'Обновлён',
            "started": 'Запущен',
            "finished": 'Завершён',
            "stopped": 'Остановлен',
            "error": 'Ошибка',
        }
        name_models = {
            "master_worker": 'Модель мастер-воркер',
            "island_model": 'Островная модель',
            "asynchronous_model": 'Асинхронная модель',
        }
        task_config = {
            "algorithm": 'Алгоритм',
            "num_islands": 'Количество островов',
            "num_workers": 'Количество рабочих процессов',
            "mutation_rate": 'Вероятность мутации',
            "crossover_rate": 'Вероятность кроссинговера',
            "fitness_kwargs": 'Аргументы функции приспособленности',
            "selection_rate": 'Вероятность отбора особей',
            "migration_rate": 'Доля популяции для миграции',
            "max_generations": 'Максимальное количество поколений',
            "mutation_kwargs": 'Аргументы функции мутации',
            "population_size": 'Размер популяции',
            "crossover_kwargs": 'Аргументы функции кроссинговера',
            "fitness_function": 'Функция приспособленности',
            "selection_kwargs": 'Аргументы функции селекции',
            "mutation_function": 'Функция мутации',
            "crossover_function": 'Функция кроссинговера',
            "migration_interval": 'Интервал миграции',
            "selection_function": 'Функция селекции',
            "termination_kwargs": 'Аргументы функции завершения',
            "termination_function": 'Функция завершения',
            "initialize_population_kwargs": 'Аргументы функции инициализации популяции',
            "initialize_population_function": 'Функция инициализации популяции',
            "adaptation_function": 'Функция адаптации',
            "adaptation_kwargs": 'Аргументы функции адаптации',
        }

        translations = {
            **statuses,
            **name_models,
            **task_config,

        }
        user = self.request.user
        user_id = user.id
        functions_mapping = self.get_functions_mapping(user_id)
        if isinstance(functions_mapping, Response):
            return functions_mapping

        functions_translate = {}
        for function_mapping in functions_mapping:
            for _, function_path in function_mapping.items():
                function_args_translate = get_translations_from_function(function_path)
                functions_translate.update(function_args_translate)

        translations.update(functions_translate)

        return Response(translations, status=status.HTTP_200_OK)
