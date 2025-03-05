import os

from rest_framework.response import Response

from api.responses import permission_denied_response, bad_request_response, not_found_response
from api.utils.custom_logger import get_user_folder_name
from api.utils.load_custom_funcs.core_function_utils import CROSSOVER_FUNCTION_MAPPING, FITNESS_FUNCTION_MAPPING, \
    MUTATION_FUNCTION_MAPPING, SELECTION_FUNCTION_MAPPING, ADAPTATION_FUNCTION_MAPPING, \
    INIT_POPULATION_FUNCTION_MAPPING, TERMINATION_FUNCTION_MAPPING
from api.utils.load_custom_funcs.load_custom_functions import get_functions_with_import_paths
from modeling_system_backend import settings

MEDIA_ROOT = settings.MEDIA_ROOT


class UserFunctionMixin:
    @staticmethod
    def get_functions_folder(user_id):
        if not user_id:
            return permission_denied_response()

        user_folder = get_user_folder_name(user_id)
        users_functions_folder = os.path.join(MEDIA_ROOT, "users_functions", user_folder)

        user_adaptation_folder = os.path.join(users_functions_folder, "custom_adaptation_funcs")
        user_crossover_folder = os.path.join(users_functions_folder, "custom_crossover_funcs")
        user_fitness_folder = os.path.join(users_functions_folder, "custom_fitness_funcs")
        user_init_population_folder = os.path.join(users_functions_folder, "custom_init_population_funcs")
        user_mutation_folder = os.path.join(users_functions_folder, "custom_mutation_funcs")
        user_selection_folder = os.path.join(users_functions_folder, "custom_selection_funcs")
        user_termination_folder = os.path.join(users_functions_folder, "custom_termination_funcs")

        return (user_adaptation_folder,
                user_crossover_folder,
                user_fitness_folder,
                user_init_population_folder,
                user_mutation_folder,
                user_selection_folder,
                user_termination_folder)

    @classmethod
    def get_functions_mapping(cls, user_id):
        functions_folder = cls.get_functions_folder(user_id)
        if isinstance(functions_folder, Response):
            return functions_folder

        (user_adaptation_folder,
         user_crossover_folder,
         user_fitness_folder,
         user_init_population_folder,
         user_mutation_folder,
         user_selection_folder,
         user_termination_folder) = functions_folder

        user_adaptation_func_mapping = get_functions_with_import_paths(user_adaptation_folder)
        adaptation_functions = {
            **ADAPTATION_FUNCTION_MAPPING,
            **user_adaptation_func_mapping
        }

        user_crossover_func_mapping = get_functions_with_import_paths(user_crossover_folder)
        crossover_functions = {
            **CROSSOVER_FUNCTION_MAPPING,
            **user_crossover_func_mapping
        }
        user_fitness_func_mapping = get_functions_with_import_paths(user_fitness_folder)
        fitness_functions = {
            **FITNESS_FUNCTION_MAPPING,
            **user_fitness_func_mapping
        }
        user_init_population_func_mapping = get_functions_with_import_paths(user_init_population_folder)
        init_population_functions = {
            **INIT_POPULATION_FUNCTION_MAPPING,
            **user_init_population_func_mapping
        }

        user_mutation_func_mapping = get_functions_with_import_paths(user_mutation_folder)
        mutation_functions = {
            **MUTATION_FUNCTION_MAPPING,
            **user_mutation_func_mapping
        }
        user_selection_func_mapping = get_functions_with_import_paths(user_selection_folder)
        selection_functions = {
            **SELECTION_FUNCTION_MAPPING,
            **user_selection_func_mapping
        }

        user_termination_func_mapping = get_functions_with_import_paths(user_termination_folder)
        termination_functions = {
            **TERMINATION_FUNCTION_MAPPING,
            **user_termination_func_mapping
        }

        return (adaptation_functions,
                crossover_functions,
                fitness_functions,
                init_population_functions,
                mutation_functions,
                selection_functions,
                termination_functions)

    @staticmethod
    def choose_func_folder(type_of_function, functions_folder):
        if not type_of_function:
            return bad_request_response(f"{type_of_function} is not valid")

        (user_adaptation_folder,
         user_crossover_folder,
         user_fitness_folder,
         user_init_population_folder,
         user_mutation_folder,
         user_selection_folder,
         user_termination_folder) = functions_folder

        match type_of_function:
            case "adaptation":
                return_folder = user_adaptation_folder
            case "crossover":
                return_folder = user_crossover_folder
            case "fitness":
                return_folder = user_fitness_folder
            case "initialize_population":
                return_folder = user_init_population_folder
            case "mutation":
                return_folder = user_mutation_folder
            case "selection":
                return_folder = user_selection_folder
            case "termination":
                return_folder = user_termination_folder
            case _:
                return not_found_response(f"{type_of_function = }")

        os.makedirs(return_folder, exist_ok=True)

        return return_folder

    @classmethod
    def get_user_function_folder(cls, type_of_function, user_id):
        functions_folder = cls.get_functions_folder(user_id)
        if isinstance(functions_folder, Response):
            return functions_folder
        user_function_folder = cls.choose_func_folder(type_of_function, functions_folder)
        return user_function_folder
