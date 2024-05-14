from django.shortcuts import render

def login(request):
  return render(request, 'login.html', {})

def signup(request):
  return render(request, 'signup.html', {})

def info(request):
  return render(request, 'info.html', {})

def history(request):
  return render(request, 'history.html', {})

def findPW(request):
  return render(request, 'findPW.html', {})
# Create your views here.
