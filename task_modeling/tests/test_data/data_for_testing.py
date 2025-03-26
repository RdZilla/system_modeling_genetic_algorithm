TEST_TASK_CONFIG = {
    "name": "test_config",
    "config": {
        'adaptation_function': '',
        'adaptation_kwargs': {},
        'algorithm': 'master_worker',
        'crossover_function': 'single_point_crossover',
        'crossover_kwargs': {},
        'crossover_rate': 0.95,
        'fitness_function': 'rastrigin_fitness',
        'fitness_kwargs': {},
        'initialize_population_function': 'random_initialization',
        'initialize_population_kwargs': {
            'chrom_length': 10,
        },
        'max_generations': 100,
        'mutation_function': 'bitwise_mutation',
        'mutation_kwargs': {},
        'mutation_rate': 0.05,
        'num_workers': 1,
        'population_size': 100,
        'selection_function': 'tournament_selection',
        'selection_kwargs': {
            'min_max_rule': 'min',
            'tournament_size': '3',
        },
        'selection_rate': 0.9,
        'termination_function': '',
        'termination_kwargs': {},
    }

}

TEST_EXPERIMENT = {
    "name": " Experiment_1_master_worker",
    "configs": [
        {
            **TEST_TASK_CONFIG
        }
    ]
}
