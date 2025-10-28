from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15)
    gender = models.CharField(
        max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Others", "Others")]
    )
    date_of_birth = models.DateField()
    address = models.TextField()
    joining_date = models.DateField()
    teacher_image = models.ImageField(upload_to="teachers/", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Fee(models.Model):
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fee for {self.student} - {self.amount}"


class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ("national", "National Holiday"),
        ("religious", "Religious Holiday"),
        ("international", "International Holiday"),
        ("special", "Special Holiday"),
        ("bank", "Bank Holiday"),
    ]

    name = models.CharField(max_length=200)
    date = models.DateField()
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default="national")
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False, help_text="If this holiday occurs every year")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        unique_together = ["name", "date"]

    def __str__(self):
        return f"{self.name} - {self.date}"

    def get_holiday_type_display_badge(self):
        """Return Bootstrap badge class based on holiday type"""
        type_badges = {
            "national": "badge-danger",
            "religious": "badge-success",
            "international": "badge-info",
            "special": "badge-warning",
            "bank": "badge-secondary",
        }
        return type_badges.get(self.holiday_type, "badge-primary")

    @property
    def is_upcoming(self):
        """Check if holiday is upcoming"""
        from django.utils import timezone

        return self.date >= timezone.now().date()

    @property
    def days_until(self):
        """Calculate days until holiday"""
        from django.utils import timezone

        if self.is_upcoming:
            delta = self.date - timezone.now().date()
            return delta.days
        return None
