from django.contrib import admin
from django.urls import include, path
from home.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('/', include('home.urls')),
    path('users/', include('users.urls'))
]
