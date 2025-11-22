from django.contrib.auth.models import User
from django.db import models
from employees.models import Department
import uuid


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    full_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    applied_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    job_position = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=0)
    education_type = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    # files
    pasport = models.FileField(upload_to='pasports/')
    diploma = models.FileField(upload_to='diplomas/')
    resume = models.FileField(upload_to='resumes/')

    reviewed_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    comments = models.TextField(blank=True, null=True)

    interview_datetime = models.DateTimeField(null=True, blank=True)

    application_code = models.CharField(max_length=20, unique=True, blank=True)


    def save(self, *args, **kwargs):
        # generate application code
        if not self.application_code:
            self.application_code = f"APP-{uuid.uuid4().hex[:8].upper()}"

        # archive if status changed
        if self.pk:
            old = JobApplication.objects.get(pk=self.pk)
            if old.status != self.status and self.status in ['accepted', 'rejected']:
                self.archive()

        super().save(*args, **kwargs)

    def archive(self):
        archive_obj = JobApplicationArchive.objects.create(
            original_id=self.id,
            full_name=self.full_name,
            email=self.email,
            phone=self.phone,
            applied_department=str(self.applied_department),
            job_position=self.job_position,
            status=self.status,
            comments=self.comments
        )

        # Fayllarni archive_files/ ichiga ko‘chirish
        if self.pasport:
            JobApplicationArchiveFile.objects.create(
                archive=archive_obj,
                file=self.pasport,
                file_type="pasport"
            )

        if self.diploma:
            JobApplicationArchiveFile.objects.create(
                archive=archive_obj,
                file=self.diploma,
                file_type="diploma"
            )

        if self.resume:
            JobApplicationArchiveFile.objects.create(
                archive=archive_obj,
                file=self.resume,
                file_type="resume"
            )

    def __str__(self):
        return f"{self.full_name} - {self.job_position}"


class JobApplicationArchive(models.Model):
    original_id = models.IntegerField()
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    applied_department = models.CharField(max_length=200)
    job_position = models.CharField(max_length=150, null=True, blank=True)

    status = models.CharField(max_length=20)
    comments = models.TextField(null=True, blank=True)
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archive {self.full_name} - {self.status}"


class JobApplicationArchiveFile(models.Model):
    archive = models.ForeignKey(
        JobApplicationArchive,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to="archive_files/")
    file_type = models.CharField(max_length=50)  # pasport, diploma, resume, cover_letter

    def __str__(self):
        return f"{self.file_type} file for {self.archive.full_name}"
