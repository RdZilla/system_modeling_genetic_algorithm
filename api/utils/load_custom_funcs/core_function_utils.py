route_to_core = "core"

route_to_core_crossover = f"{route_to_core}.crossover"
CROSSOVER_FUNCTION_MAPPING = {
}

route_to_core_fitness = f"{route_to_core}.fitness"
FITNESS_FUNCTION_MAPPING = {
    "rastrigin": f"{route_to_core_fitness}.rastrigin_fitness.rastrigin"
}

route_to_core_mutation = f"{route_to_core}.mutation"
MUTATION_FUNCTION_MAPPING = {

}
route_to_core_selection = f"{route_to_core}.selection"
SELECTION_FUNCTION_MAPPING = {

}