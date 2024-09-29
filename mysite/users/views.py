from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from urllib.parse import urlparse

from .forms import RegistrationForm
from .forms import LoginForm
from .forms import UserUpdateForm, CustomPasswordChangeForm
from .models import PrivacyPolicy


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
        
        # 사용자가 비밀번호를 변경하고자 할 때만 password_form을 처리
        if user_form.is_valid():
            if password_form.is_valid():
                # 비밀번호 필드가 비어있지 않을 때만 비밀번호 변경 처리
                new_password1 = password_form.cleaned_data.get('new_password1')
                new_password2 = password_form.cleaned_data.get('new_password2')

                if new_password1 or new_password2:
                    user = password_form.save()
                    update_session_auth_hash(request, user)  # 비밀번호 변경 시 세션 갱신

            user_form.save()
            messages.success(request, '회원 정보가 수정되었습니다.')
            return redirect('info')
        
        else:
            print(user_form.errors)  # user_form의 오류 출력
            print(password_form.errors)  # password_form의 오류 출력
            messages.error(request, '오류가 발생했습니다. 모든 폼을 올바르게 작성했는지 확인하세요.')
  else:
        user_form = UserUpdateForm(instance=request.user) 
        password_form = CustomPasswordChangeForm(request.user)
        
  context = {
        'user_form': user_form,
        'password_form': password_form
    }           
  
  return render(request, 'info.html', context)

# Create your views here.
