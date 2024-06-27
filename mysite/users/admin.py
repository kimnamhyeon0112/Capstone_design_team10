from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Django's built-in user model requires user ID, as opposed to what we're trying to do
# Changing the custom model means having to implement custom admin as well
# https://tech.serhatteker.com/post/2020-01/email-as-username-django/
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Register your models here.
admin.site.register(User, CustomUserAdmin)
