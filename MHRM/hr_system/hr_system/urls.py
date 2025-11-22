from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="HR Recruitment API",
        default_version='v1',
        description="Ishga qabul qilish tizimi uchun API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger JSON/YAML endpoints
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

    # ReDoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    # Application APIs
    path('api/', include('applications.urls')),
    path('api/dep/', include('employees.urls')),
]
