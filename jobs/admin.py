from django.contrib import admin
from .models import JobPost, JobApplication


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('required_skill', 'thekedar', 'duration_days', 'wage_offer', 'status', 'created_at')
    list_filter = ('status', 'required_skill', 'created_at')
    search_fields = ('thekedar__company_name', 'required_skill__name')
    date_hierarchy = 'created_at'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('worker', 'job', 'status', 'applied_date')
    list_filter = ('status', 'applied_date')
    search_fields = ('worker__user__name', 'job__required_skill__name')
    date_hierarchy = 'applied_date'
