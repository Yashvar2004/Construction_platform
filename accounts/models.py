from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('worker', 'Worker'),
        ('thekedar', 'Thekedar'),
        ('user', 'Normal User'),
    ]
    
    username = None  # Remove username field
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'role', 'location']
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"
