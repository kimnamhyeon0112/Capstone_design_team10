from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

# Quick references:
# Specifics about PostgreSQL https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes
# Django's built-in authentication https://docs.djangoproject.com/en/5.0/topics/auth/default/
# Django's DB tutorial https://docs.djangoproject.com/en/5.0/intro/tutorial02/

# Steps to update models
# 1. Make changes to models.py
# 2. Create migrations:
# python manage.py makemigrations users
# 3. Applying migrations:
# python manage.py migrate

# Models used in the app.
# By default, Django includes a numeric ID when creating new models, used as a primary key.

# For storing user data, Django conveniently has one built-in:
# https://docs.djangoproject.com/en/5.0/topics/auth/default/
# django.contrib.auth.models.user
# However it is good practice to create a custom user model for futureproofing
# (See https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#specifying-a-custom-user-model)

# Django's built-in user model requires user ID, as opposed to what we're trying to do
# https://tech.serhatteker.com/post/2020-01/email-as-username-django/

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email not set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)

        if extra.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra)

class User(AbstractUser):
    username = None
    email = models.EmailField("E-mail address", unique=True)
    display_name = models.CharField('Name', max_length=30, blank=True, null=True)
    nickname = models.CharField(max_length=30, blank=True)
    additional_email = models.EmailField('Additional E-mail address', blank=True, null=True)
    contact_number = models.CharField('Contact Number', max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    pass

'''class Website(models.Model):
    # Name of the website
    name = models.CharField(max_length=255)
    # Link to the privacy policy.
    # Not sure how long of a URL we should allow?
    link = models.CharField(max_length=1024)
    pass'''

class PrivacyPolicy(models.Model):
    # The list of things we need:
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    url = models.URLField(max_length=200, null=True)
    site_name = models.CharField(max_length=100, blank=True)
    summary_date = models.DateTimeField(auto_now_add=True)
    # PK of the website - FOREIGN KEY
    #website = models.ForeignKey(Website, on_delete=models.CASCADE)
    # Full content
    full_text = models.TextField()
    # Summarised content
    summary = models.TextField(blank=True, null=True)
    pass

'''class UserHistory(models.Model):
    # PK of the user- FOREIGN KEY
    # See https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#referencing-the-user-model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # PK of privacy policy - FOREIGN KEY
    policy = models.ForeignKey(PrivacyPolicy, on_delete=models.CASCADE)
    pass'''