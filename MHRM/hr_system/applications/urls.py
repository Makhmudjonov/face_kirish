from django.urls import path
from .views import (
    JobApplicationPublicCreateAPIView,
    AdminApplicationDetailAPIView,
    ArchiveListAPIView,
    ArchiveDetailAPIView, JobApplicationAdminViewSet
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'admin/applications', JobApplicationAdminViewSet, basename='admin-applications')
urlpatterns = [
    # Public
    path('applications/apply/', JobApplicationPublicCreateAPIView.as_view()),
    path('admin/applications/<int:pk>/', AdminApplicationDetailAPIView.as_view()),

    # Archive
    path('admin/archive/', ArchiveListAPIView.as_view()),
    path('admin/archive/<int:pk>/', ArchiveDetailAPIView.as_view()),
] + router.urls
