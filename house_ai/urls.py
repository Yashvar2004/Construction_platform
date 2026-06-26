from django.urls import path
from . import views

app_name = 'house_ai'

urlpatterns = [
    path('submit/', views.submit_requirement, name='submit'),
    path('upload-media/<int:requirement_id>/', views.upload_media, name='upload_media'),
    path('my-requirements/', views.my_requirements, name='my_requirements'),
    path('view/<int:requirement_id>/', views.view_requirement, name='view_requirement'),
    path('delete-media/<int:media_id>/', views.delete_media, name='delete_media'),
    path('regenerate-ai/<int:requirement_id>/', views.regenerate_ai_response, name='regenerate_ai'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('explore-designs/<int:requirement_id>/', views.explore_designs, name='explore_designs'),
]
