from django.urls import path
from . import views

urlpatterns = [
  path('login', views.login, name="login"),
  path('signup', views.signup, name="signup"),
  path('info', views.info, name="info"),
  path('history', views.history, name="history"),
  path('findPW', views.findPW, name="findPW")
]