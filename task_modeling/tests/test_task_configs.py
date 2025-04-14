import json
import pytest
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from task_modeling.models import TaskConfig
from task_modeling.serializers import TaskConfigSerializer
from task_modeling.tests.test_data.data_for_testing import TEST_TASK_CONFIG

User = get_user_model()


@pytest.fixture
def user(db):
    """Создает тестового пользователя"""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def client(user):
    """Возвращает аутентифицированного клиента"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def setup_task_configs(db, user):
    """Создает тестовые объекты TaskConfig"""
    task_configs = [TaskConfig.objects.create(**TEST_TASK_CONFIG, user=user) for _ in range(3)]
    return task_configs


@pytest.fixture
def clean_db(db):
    """Удаляет все объекты перед тестами (чтобы не было ошибок уникальности)"""
    TaskConfig.objects.all().delete()


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(1)
def test_get_all_task_configs(client, setup_task_configs):
    response = client.get(reverse("list_configs_create_config"))

    assert response.status_code == status.HTTP_200_OK
    results_data = response.data.get("results")
    assert len(setup_task_configs) == len(results_data)

    for number, task_config in enumerate(setup_task_configs):
        expected_data = TaskConfigSerializer(instance=task_config).data
        assert results_data[number]["name"] == expected_data["name"]
        assert results_data[number]["config"] == expected_data["config"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(2)
def test_delete_task_config(client, setup_task_configs):
    for task_config in setup_task_configs:
        task_config_id = task_config.id
        response = client.delete(reverse("task_config_management", args=[task_config_id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    assert TaskConfig.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(3)
def test_post_task_config(client, clean_db):
    response = client.post(
        reverse("list_configs_create_config"),
        data=json.dumps(TEST_TASK_CONFIG),
        content_type="application/json"
    )
    assert response.status_code == status.HTTP_201_CREATED

    assert TaskConfig.objects.count() == 1
    created_task_config = TaskConfig.objects.first()
    assert created_task_config.name == TEST_TASK_CONFIG["name"]
    assert created_task_config.config == TEST_TASK_CONFIG["config"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(4)
def test_get_task_config_by_id(client, setup_task_configs):
    task_config = setup_task_configs[0]
    response = client.get(reverse("task_config_management", args=[task_config.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == TaskConfigSerializer(task_config).data


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(5)
def test_get_nonexistent_task_config(client):
    response = client.get(reverse("task_config_management", args=[9999999999]))  # Несуществующий ID

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(6)
def test_delete_nonexistent_task_config(client):
    response = client.delete(reverse("task_config_management", args=[9999999999]))  # Несуществующий ID

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(7)
def test_post_invalid_task_config(client):
    invalid_data = {
        "config": {  # Нет "name"
            "algorithm": "master_worker",
            "generations": 100
        }
    }
    response = client.post(
        reverse("list_configs_create_config"),
        data=json.dumps(invalid_data),
        content_type="application/json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(8)
def test_patch_task_config(client, setup_task_configs):
    task_config = setup_task_configs[0]
    update_data = {"name": "updated_name"}

    response = client.patch(
        reverse("task_config_management", args=[task_config.id]),
        data=json.dumps(update_data),
        content_type="application/json"
    )

    assert response.status_code == status.HTTP_200_OK
    task_config.refresh_from_db()
    assert task_config.name == "updated_name"


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(9)
def test_put_task_config(client, setup_task_configs):
    task_config = setup_task_configs[0]
    new_data = {
        "name": "completely_new_config",
        "config": {
            'adaptation_function': '',
            'adaptation_kwargs': {},
            'algorithm': 'master_worker',
            'crossover_function': 'single_point_crossover',
            'crossover_kwargs': {},
            'crossover_rate': 0.85,
            'fitness_function': 'rastrigin_fitness',
            'fitness_kwargs': {},
            'initialize_population_function': 'random_init',
            'initialize_population_kwargs': {
                'chrom_length': 8,
            },
            'max_generations': 50,
            'mutation_function': 'bitwise_mutation',
            'mutation_kwargs': {},
            'mutation_rate': 0.01,
            'population_size': 50,
            'selection_function': 'tournament_selection',
            'selection_kwargs': {
                'min_max_rule': 'min',
                'tournament_size': '5',
            },
            'selection_rate': 0.95,
            'termination_function': '',
            'termination_kwargs': {},
        }
    }

    response = client.put(
        reverse("task_config_management", args=[task_config.id]),
        data=json.dumps(new_data),
        content_type="application/json"
    )

    assert response.status_code == status.HTTP_200_OK
    task_config.refresh_from_db()
    assert task_config.name == new_data["name"]
    assert task_config.config == new_data["config"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.order(10)
def test_put_invalid_task_config(client, setup_task_configs):
    task_config = setup_task_configs[0]
    invalid_data = TEST_TASK_CONFIG  # Дубликат

    response = client.put(
        reverse("task_config_management", args=[task_config.id]),
        data=json.dumps(invalid_data),
        content_type="application/json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
