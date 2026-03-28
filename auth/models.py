from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Additional fields for the User model
    # Example: phone_number = models.CharField(max_length=15, blank=True, null=True)
    pass

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Other fields for student profile
    grade_level = models.CharField(max_length=10)
    major = models.CharField(max_length=100, blank=True)
    # Example: address = models.CharField(max_length=255, blank=True, null=True)
