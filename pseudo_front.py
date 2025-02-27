import requests
import json

request_url_base = "http://localhost:8000/api/v1/tasks_module"
auth_credentials = ("admin", "admin")


# =======================================================
def print_response(response):
    response = response.json()
    response = json.dumps(response, indent=4)
    print(response)


# =======================================================
def get_request(request_url):
    response = requests.get(request_url, auth=auth_credentials)
    print_response(response)


def post_request(request_url, data: dict):
    response = requests.post(request_url, json=data, auth=auth_credentials)
    print_response(response)


def delete_request(request_url):
    response = requests.delete(request_url, auth=auth_credentials)
    print_response(response)


# =======================================================

# =======================================================
def get_task_config(task_config_id=None):
    request_url = f"{request_url_base}/task_config"
    if task_config_id:
        request_url += f"/{task_config_id}"
    get_request(request_url)


def post_task_config():
    request_url = f"{request_url_base}/task_config"
    request_data = {
        "name": "test_task_config",
        "config": {
            "algorithm": "master_worker",
            "generations": 100,
            "mutation_rate": 0.05,
            "crossover_rate": 0.9,
            "population_size": 200,
            "fitness_function": "rastrigin"
        },
        "user": "1",
    }
    post_request(request_url, request_data)


# =======================================================
def get_experiment(experiment_id=None, start=False):
    request_url = f"{request_url_base}/experiment"
    if experiment_id:
        request_url += f"/{experiment_id}?{start=}"

    get_request(request_url)


def post_experiment():
    request_url = f"{request_url_base}/experiment"
    request_data = {
        "name": "Task name",
        "user": "1",
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
    post_request(request_url, request_data)


def delete_experiment(experiment_id):
    request_url = f"{request_url_base}/experiment/{experiment_id}"
    delete_request(request_url)


# =======================================================

if __name__ == "__main__":
    # ======================================
    # get_experiment()
    get_experiment(experiment_id=7, start=True)
    # post_experiment()
    # delete_experiment(experiment_id=7)
    # =======================================

    # get_task_config()
    # post_task_config()

    pass
