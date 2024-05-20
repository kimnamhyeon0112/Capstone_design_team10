from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {})

def summary(request):
    return render(request, 'summary.html', {})
# Create your views here.
