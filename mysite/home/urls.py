from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summary/<int:pk>/', views.summary_detail, name='summary_detail'),
    path('history/', views.history, name="history"),
    path('history/update_check_status/', views.update_check_status, name='update_check_status'),
    path('delete/', views.delete_policy, name='delete_policy'),
]