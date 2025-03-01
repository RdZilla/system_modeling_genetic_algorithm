# import pytest
# from django.contrib.auth.models import User
# from rest_framework.test import APIClient
#
# from task_modeling.models import Experiment
# from task_modeling.tests.test_data.data_for_testing import TEST_EXPERIMENT
#
#
# @pytest.fixture
# def user(db):
#     """Создает тестового пользователя"""
#     return User.objects.create_user(username="testuser", password="testpass")
#
#
# @pytest.fixture
# def client(user):
#     """Возвращает аутентифицированного клиента"""
#     client = APIClient()
#     client.force_authenticate(user=user)
#     return client
#
# @pytest.fixture
# def setup_experiments(db, user):
#     """Создает тестовые объекты TaskConfig"""
#     task_configs = [Experiment.objects.create(**TEST_EXPERIMENT, user=user) for _ in range(3)]
#     return task_configs