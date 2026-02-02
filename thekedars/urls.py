from django.urls import path
from . import views

app_name = 'thekedars'

urlpatterns = [
    path('profile/', views.thekedar_profile, name='profile'),
    path('create-project/', views.create_project, name='create_project'),
    path('projects/', views.projects_list, name='projects'),
    path('edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('create-job/', views.create_job_post, name='create_job'),
    path('job-posts/', views.job_posts_list, name='job_posts'),
    path('job-applications/<int:job_id>/', views.job_applications, name='job_applications'),
    path('application/<int:application_id>/<str:action>/', views.update_application_status, name='update_application'),
]
