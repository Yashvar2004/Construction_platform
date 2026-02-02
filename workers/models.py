from django.db import models
from accounts.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    experience_years = models.PositiveIntegerField()
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    skills = models.ManyToManyField(Skill, through='WorkerSkillMap')
    
    def __str__(self):
        return f"{self.user.name} - Worker"


class WorkerSkillMap(models.Model):
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['worker', 'skill']
    
    def __str__(self):
        return f"{self.worker.user.name} - {self.skill.name}"
