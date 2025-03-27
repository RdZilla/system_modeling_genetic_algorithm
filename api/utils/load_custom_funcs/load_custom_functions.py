import ast
import os
import importlib.util
import inspect

import logging

from modeling_system_backend.settings import BASE_DIR


debug_looger = logging.getLogger("common")

def extract_kwargs_params_from_module_path(module_path):
    """Принимает путь в формате 'path.to.your.file' и возвращает список параметров, использующихся через kwargs.get()."""
    params = set()
    try:
        # Преобразуем модульный путь в путь к файлу и название функции
        function_route = [*module_path.split(".")]

        file_route = function_route[:-1]
        debug_looger.info(f"{file_route}] Start scanning")

        function_name = function_route[-1]
        file_path = os.path.join(BASE_DIR, *file_route) + ".py"

        with open(file_path, "r", encoding="utf-8") as f:
            file_code = f.read()

        # Разбираем файл в AST
        tree = ast.parse(file_code)

        # Ищем конкретную функцию в AST
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Ищем внутри функции все вызовы kwargs.get()
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call) and isinstance(sub_node.func, ast.Attribute):

                        debug_looger.info(f"[{file_route}]    {sub_node.func.attr = }")

                        if sub_node.func.attr == 'get':
                            if len(sub_node.args) > 0:
                                arg = sub_node.args[0]

                                debug_looger.info(f"{file_route}]    {arg.s = } | {arg.value = }")

                                if isinstance(arg, ast.Str):  # Python < 3.8
                                    params.add(arg.s)

                                    debug_looger.info(f"{file_route}]    APPEND")

                                elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):  # Python >= 3.8
                                    params.add(arg.value)

                                    debug_looger.info(f"{file_route}]    APPEND")
                break  # Нашли функцию — выходим из цикла

    except FileNotFoundError:
        print(f"Файл {module_path} не найден.")
    except Exception as e:
        print(f"Ошибка при обработке файла {module_path}: {e}")

    return list(params)


def get_functions_with_import_paths(folder_path):
    functions_dict = {}

    try:
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".py"):
                file_path = os.path.join(folder_path, file_name)
                module_name = file_name[:-3]

                relative_module_path = os.path.relpath(file_path, start=BASE_DIR).replace(os.path.sep, ".")[:-3]

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                functions = inspect.getmembers(module, inspect.isfunction)

                for function_name, _ in functions:
                    function_path = f"{relative_module_path}.{function_name}"
                    functions_dict[function_name] = function_path
    except FileNotFoundError:
        pass

    return functions_dict
