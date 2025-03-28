from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_version = 1
api_url = "api/v1/"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(api_version=api_version), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

    path(api_url + 'auth/', include('authorization.urls')),
    path(api_url + 'task_module/', include('task_modeling.urls')),
]
