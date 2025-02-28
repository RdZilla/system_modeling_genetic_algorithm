TEST_TASK_CONFIG = {
    "name": "test_task_config",
    "config": {
        "algorithm": "master_worker",
        "generations": 100,
        "mutation_rate": 0.05,
        "crossover_rate": 0.9,
        "population_size": 200,
        "fitness_function": "rastrigin"
    }
}

TEST_EXPERIMENT = {
        "name": "Task name",
        "configs": [
            {
                "name": "config_name",
                "config": {
                    "algorithm": "master_worker",
                    "generations": 100,
                    "mutation_rate": 0.05,
                    "crossover_rate": 0.9,
                    "population_size": 200,
                    "fitness_function": "rastrigin"
                }
            },
            {
                "name": "config_name",
                "config": {
                    "algorithm": "master_worker",
                    "generations": 100,
                    "mutation_rate": 0.05,
                    "crossover_rate": 0.9,
                    "population_size": 200,
                    "fitness_function": "rastrigin"
                }
            }
        ]
    }