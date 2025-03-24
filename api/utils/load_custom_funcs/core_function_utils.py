import os.path

from api.utils.load_custom_funcs.load_custom_functions import get_functions_with_import_paths

from core.models.asynchronous_model import AsynchronousGA
from core.models.island_model import IslandGA
from core.models.master_worker_model import MasterWorkerGA

from modeling_system_backend.settings import BASE_DIR

SUPPORTED_MODELS_GA = {
    "master_worker": MasterWorkerGA,
    "island_model": IslandGA,
    "asynchronous_model": AsynchronousGA
}

route_to_core = os.path.join(BASE_DIR, "core")

route_to_core_adaptation = os.path.join(route_to_core, "adaptation")
ADAPTATION_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_adaptation)

route_to_core_crossover = os.path.join(route_to_core, "crossover")
CROSSOVER_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_crossover)

route_to_core_fitness = os.path.join(route_to_core, "fitness")
FITNESS_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_fitness)

route_to_core_init_population = os.path.join(route_to_core, "init_population")
INIT_POPULATION_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_init_population)

route_to_core_mutation = os.path.join(route_to_core, "mutation")
MUTATION_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_mutation)

route_to_core_selection = os.path.join(route_to_core, "selection")
SELECTION_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_selection)

route_to_core_termination = os.path.join(route_to_core, "termination")
TERMINATION_FUNCTION_MAPPING = get_functions_with_import_paths(route_to_core_termination)
