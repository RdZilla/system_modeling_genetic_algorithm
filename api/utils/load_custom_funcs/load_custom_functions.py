import os
import importlib.util
import inspect

from  modeling_system_backend.settings import BASE_DIR

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
