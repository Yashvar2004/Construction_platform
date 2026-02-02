from django.db import models
from accounts.models import User


class HouseRequirement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='house_requirements')
    plot_size = models.CharField(max_length=50)  # e.g., "1000 sq ft"
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    floors = models.PositiveIntegerField(default=1)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.city} ({self.plot_size})"


class MediaUpload(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    requirement = models.ForeignKey(HouseRequirement, on_delete=models.CASCADE, related_name='media_uploads')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    file_path = models.FileField(upload_to='house_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.requirement.user.name} - {self.media_type}"


class AIResponse(models.Model):
    requirement = models.OneToOneField(HouseRequirement, on_delete=models.CASCADE, related_name='ai_response')
    design_suggestion = models.TextField()
    cost_insight = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AI Response for {self.requirement.user.name}"
