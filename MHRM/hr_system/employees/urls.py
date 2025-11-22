from django.urls import path
from .views import DepartmentListAPI

urlpatterns = [
    path('departments/', DepartmentListAPI.as_view(), name='department-list'),
]
