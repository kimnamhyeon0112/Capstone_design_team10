from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from .forms import RegistrationForm
from .forms import LoginForm
from .forms import UserUpdateForm, CustomPasswordChangeForm


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
  if not request.user.is_authenticated:
        return redirect('login')
      
  if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        
        if user_form.is_valid() and password_form.is_valid():
          user_form.save()
          user = password_form.save()
          update_session_auth_hash(request, user)
          messages.success(request, f'회원 정보가 수정 되었습니다.')
          return redirect('info')
        
        else:
            messages.error(request, '오류가 발생했습니다. 모든 폼을 올바르게 작성했는지 확인하세요.')
  else:
        user_form = UserUpdateForm(instance=request.user) 
        password_form = CustomPasswordChangeForm(request.user)
        
  context = {
        'user_form': user_form,
        'password_form': password_form
    }           
  
  return render(request, 'info.html', context)

def history(request):
  return render(request, 'history.html', {})
# Create your views here.
