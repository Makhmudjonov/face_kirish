from rest_framework import generics
from employees.models import Department
from .serializers import DepartmentSerializer

class DepartmentListAPI(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
