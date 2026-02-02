from django.contrib import admin
from .models import ThekedarProfile, Project


@admin.register(ThekedarProfile)
class ThekedarProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'experience_years', 'score', 'verified')
    list_filter = ('verified', 'experience_years')
    search_fields = ('user__name', 'company_name')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'thekedar', 'budget', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'thekedar__company_name')
    date_hierarchy = 'created_at'
