from django.urls import path
from .views import RegisterView, EmailTokenObtainPairView, SendCodeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('send-code', SendCodeView.as_view(), name='send-code'),
    path('login', EmailTokenObtainPairView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
]
