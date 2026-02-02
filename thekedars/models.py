from django.db import models
from accounts.models import User


class ThekedarProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='thekedar_profile')
    experience_years = models.PositiveIntegerField()
    company_name = models.CharField(max_length=200)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.name} - Thekedar ({self.company_name})"


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    thekedar = models.ForeignKey(ThekedarProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.thekedar.company_name}"
