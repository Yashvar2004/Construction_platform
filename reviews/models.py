from django.db import models
from accounts.models import User


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveIntegerField()  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['reviewer', 'reviewed_user']
    
    def __str__(self):
        return f"{self.reviewer.name} -> {self.reviewed_user.name} ({self.rating}/5)"
