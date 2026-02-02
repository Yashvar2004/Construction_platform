from django.contrib import admin
from .models import HouseRequirement, MediaUpload, AIResponse


@admin.register(HouseRequirement)
class HouseRequirementAdmin(admin.ModelAdmin):
    list_display = ('user', 'plot_size', 'budget', 'floors', 'city', 'created_at')
    list_filter = ('city', 'floors', 'created_at')
    search_fields = ('user__name', 'city')
    date_hierarchy = 'created_at'


@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'media_type', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at')


@admin.register(AIResponse)
class AIResponseAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'created_at')
    date_hierarchy = 'created_at'
