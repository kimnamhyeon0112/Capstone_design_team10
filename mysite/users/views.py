from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import RegistrationForm

def login(request):
  return render(request, 'login.html', {})

# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#html_forms
def signup(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)

    if form.is_valid():
      get_user_model().objects.create_user(email=form.cleaned_data["email"], password=form.cleaned_data["password"],
                                            last_name=form.cleaned_data["display_name"])
      return HttpResponseRedirect(reverse("login"))
  else:
    form = RegistrationForm()

  context = {
    'form': form
  }

  return render(request, 'signup.html', context)

def info(request):
  return render(request, 'info.html', {})

def history(request):
  return render(request, 'history.html', {})

def findPW(request):
  return render(request, 'findPW.html', {})
# Create your views here.
