# applications/serializers.py

from rest_framework import serializers
from .models import JobApplication, JobApplicationArchiveFile, JobApplicationArchive


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'full_name', 'birth_date', 'address', 'email', 'phone',
            'applied_department', 'job_position', 'experience_years',
            'pasport', 'diploma', 'resume', 'education_type'
        ]


class JobApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'id', 'application_code', 'full_name', 'job_position',
            'applied_department', 'submitted_at', 'status'
        ]


class JobApplicationDetailSerializer(serializers.ModelSerializer):
    """Ariza tafsilotlarini chiqarish va yangilash uchun"""

    # Bu maydonlarni o'zgartirish faqat PATCH/PUT so'rovlari uchun ruxsat beriladi
    # va faqat adminlar tomonidan boshqariladi.

    class Meta:
        model = JobApplication
        fields = '__all__'
        # Admin o'zgartirishi mumkin bo'lgan maydonlar (PATCH uchun)
        read_only_fields = [
            'full_name', 'birth_date', 'address', 'email', 'phone',
            'applied_department', 'job_position', 'experience_years',
            'education_type', 'submitted_at', 'pasport', 'diploma', 'resume',
            'reviewed_at', 'reviewed_by', 'application_code'
        ]


class StatusUpdateSerializer(serializers.ModelSerializer):
    """Faqat status va izohni yangilash uchun"""

    class Meta:
        model = JobApplication
        fields = ['status', 'comments']

    def update(self, instance, validated_data):
        # Statusni yangilash
        instance.status = validated_data.get('status', instance.status)

        # Izohni yangilash (Admin yozadi)
        instance.comments = validated_data.get('comments', instance.comments)

        # O'zgarishlarni saqlash, bu save() methodini chaqiradi va archive() ishlaydi
        instance.save()
        return instance


class InterviewScheduleSerializer(serializers.ModelSerializer):
    """Faqat intervyu vaqtini belgilash uchun"""

    class Meta:
        model = JobApplication
        fields = ['interview_datetime']

    def update(self, instance, validated_data):
        # Intervyu vaqtini yangilash (Admin belgilaydi)
        instance.interview_datetime = validated_data.get('interview_datetime', instance.interview_datetime)
        instance.save(update_fields=['interview_datetime'])
        return instance


class JobApplicationArchiveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplicationArchiveFile
        fields = ['file_type', 'file']

class JobApplicationArchiveSerializer(serializers.ModelSerializer):
    files = JobApplicationArchiveFileSerializer(many=True)

    class Meta:
        model = JobApplicationArchive
        fields = [
            'id', 'original_id', 'full_name', 'email', 'phone',
            'applied_department', 'job_position', 'status',
            'comments', 'archived_at', 'files'
        ]