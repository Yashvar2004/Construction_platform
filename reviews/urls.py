from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('create-worker-review/<int:worker_id>/', views.create_worker_review, name='create_worker_review'),
    path('create-thekedar-review/<int:thekedar_id>/', views.create_thekedar_review, name='create_thekedar_review'),
    path('worker-reviews/<int:worker_id>/', views.worker_reviews, name='worker_reviews'),
    path('thekedar-reviews/<int:thekedar_id>/', views.thekedar_reviews, name='thekedar_reviews'),
    path('update/<int:review_id>/', views.update_review, name='update_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('stats/<str:target_type>/<int:target_id>/', views.get_review_stats, name='get_stats'),
]
