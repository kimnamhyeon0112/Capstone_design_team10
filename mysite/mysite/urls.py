from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from home.views import home
from django.contrib.auth import views as auth_views

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('users/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('', home),
    path('/', include('home.urls')),
    path('', include('users.urls')),
    prefix_default_language=True
)
