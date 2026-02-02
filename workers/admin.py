from django.contrib import admin
from .models import Skill, WorkerProfile, WorkerSkillMap


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'daily_wage', 'availability', 'avg_rating')
    list_filter = ('availability', 'skills')
    search_fields = ('user__name', 'user__email')
    filter_horizontal = ('skills',)


@admin.register(WorkerSkillMap)
class WorkerSkillMapAdmin(admin.ModelAdmin):
    list_display = ('worker', 'skill')
    list_filter = ('skill',)
