# applications/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from .serializers import JobApplicationCreateSerializer, JobApplicationArchiveSerializer, StatusUpdateSerializer, \
    InterviewScheduleSerializer
from rest_framework import generics, permissions
from .models import JobApplication, JobApplicationArchive
from .serializers import (
    JobApplicationListSerializer,
    JobApplicationDetailSerializer
)
from rest_framework.decorators import action

from django.utils import timezone


class JobApplicationPublicCreateAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = JobApplicationCreateSerializer(data=request.data)

        if serializer.is_valid():
            # 1. Объектни сақланг ва уни бир ўзгарувчига сақлаб олинг
            # serializer.save() чақирилганда, янги яратилган JobApplication инстанси қайтарилади
            instance = serializer.save()

            # 2. Жавобга application_code ва ID ни қўшинг
            return Response({
                "message": "Ariza muvaffaqiyatli yuborildi!",
                "application_code": instance.application_code,  # <--- ҚЎШИЛДИ
                "id": instance.id  # (Қўшимча, лекин фойдали)
            }, status=status.HTTP_201_CREATED)

        # Агар validation хато бўлса
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminApplicationListAPIView(generics.ListAPIView):
    queryset = JobApplication.objects.all().order_by('-submitted_at')
    serializer_class = JobApplicationListSerializer
    # permission_classes = [permissions.IsAdminUser]


class AdminApplicationDetailAPIView(generics.RetrieveAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationDetailSerializer
    # permission_classes = [permissions.IsAdminUser]


# class AdminApplicationStatusUpdateAPIView(generics.UpdateAPIView):
#     queryset = JobApplication.objects.all()
#     serializer_class = JobApplicationStatusUpdateSerializer
#     # permission_classes = [permissions.IsAdminUser]
#
#
# class AdminApplicationInterviewAPIView(generics.UpdateAPIView):
#     queryset = JobApplication.objects.all()
#     serializer_class = JobApplicationInterviewSerializer
#     # permission_classes = [permissions.IsAdminUser]


class ArchiveListAPIView(generics.ListAPIView):
    queryset = JobApplicationArchive.objects.all().order_by('-archived_at')
    serializer_class = JobApplicationArchiveSerializer
    # permission_classes = [permissions.IsAdminUser]


class ArchiveDetailAPIView(generics.RetrieveAPIView):
    queryset = JobApplicationArchive.objects.all()
    serializer_class = JobApplicationArchiveSerializer
    # permission_classes = [permissions.IsAdminUser]


class JobApplicationAdminViewSet(viewsets.ModelViewSet):
    """
    Admin paneli uchun arizalarni boshqarish ViewSet'i.
    Faol arizalarni chiqarish va ularni o'zgartirishni boshqaradi.
    """

    # Faqat arxivga olinmagan arizalarni ko'rsatish
    queryset = JobApplication.objects.all().order_by('-submitted_at')

    # Har xil harakatlar uchun har xil serializatorlar
    def get_serializer_class(self):
        if self.action == 'list':
            return JobApplicationListSerializer
        elif self.action in ['status_update']:
            return StatusUpdateSerializer
        elif self.action in ['interview_schedule']:
            return InterviewScheduleSerializer
        return JobApplicationDetailSerializer  # retrieve/create/update uchun

    # 1. Arizaning statusini o'zgartirish (Arxivga o'tkazish logikasi modelda)
    @action(detail=True, methods=['patch'], url_path='status-update')
    def status_update(self, request, pk=None):
        """Ariza statusini (pending, accepted, rejected) yangilash va izoh qo'shish."""
        application = get_object_or_404(JobApplication, pk=pk)
        serializer = StatusUpdateSerializer(application, data=request.data, partial=True)

        if serializer.is_valid():
            # Admin kimligini avtomatik yozish (agar Authentication mavjud bo'lsa)
            # Hozircha oddiy user bilan almashtiramiz:
            # serializer.validated_data['reviewed_by'] = request.user

            updated_application = serializer.save(reviewed_at=timezone.now())

            # Agar status accepted yoki rejected ga o'zgarsa, archive() methodi modelda ishlaydi.

            # Qaytishda to'liq detal serializatorini ishlatamiz
            return Response(JobApplicationDetailSerializer(updated_application).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Arizaga intervyu vaqtini belgilash
    @action(detail=True, methods=['patch'], url_path='interview-schedule')
    def interview_schedule(self, request, pk=None):
        """Ariza uchun suhbat vaqtini belgilash."""
        application = get_object_or_404(JobApplication, pk=pk)
        serializer = InterviewScheduleSerializer(application, data=request.data, partial=True)

        if serializer.is_valid():
            updated_application = serializer.save()
            # Qaytishda to'liq detal serializatorini ishlatamiz
            return Response(JobApplicationDetailSerializer(updated_application).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Admin paneli uchun GET /api/admin/applications/ID/ so'rovini override qilamiz
    # Chunki u faqat bitta arizaning tafsilotlarini chiqaradi (Detail View).
    def retrieve(self, request, pk=None):
        application = get_object_or_404(JobApplication, pk=pk)
        serializer = JobApplicationDetailSerializer(application)
        return Response(serializer.data)