from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__name', 'reviewed_user__name')
    date_hierarchy = 'created_at'
