from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import RegistrationForm
from .forms import LoginForm

def login(request):
  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      user = authenticate(request, email=email, password=password)
      if user is not None:
        auth_login(request, user)
        return redirect(reverse('home'))  # 로그인 후 리다이렉트할 URL
      else:
        form.add_error(None, "이메일 또는 비밀번호가 잘못되었습니다.")
  else:
    form = LoginForm()
  return render(request, 'login.html', {'form':form})

def logout(request):
    auth_logout(request)
    return redirect(reverse('home'))

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
