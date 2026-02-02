from django.urls import path
from . import views

app_name = 'workers'

urlpatterns = [
    path('profile/', views.worker_profile, name='profile'),
    path('manage-skills/', views.manage_skills, name='manage_skills'),
    path('browse-jobs/', views.browse_jobs, name='browse_jobs'),
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
