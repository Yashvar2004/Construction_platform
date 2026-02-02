from django.db import models
from accounts.models import User
from thekedars.models import ThekedarProfile
from workers.models import Skill


class JobPost(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
    ]
    
    thekedar = models.ForeignKey(ThekedarProfile, on_delete=models.CASCADE, related_name='job_posts')
    required_skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    duration_days = models.PositiveIntegerField()
    wage_offer = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.required_skill.name} - {self.thekedar.company_name}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey('workers.WorkerProfile', on_delete=models.CASCADE, related_name='job_applications')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['job', 'worker']
    
    def __str__(self):
        return f"{self.worker.user.name} - {self.job.required_skill.name}"
