from django.urls import path
from .views import flower_redirect

urlpatterns = [
    path("", flower_redirect, name="flower"),
]
