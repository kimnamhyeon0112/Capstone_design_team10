from django.shortcuts import render, redirect, get_object_or_404
from .forms import SummaryForm
from users.models import PrivacyPolicy
from urllib.parse import urlparse
from django.http import JsonResponse

def home(request):
    if request.method == 'POST':
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = SummaryForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
             # URL에서 사이트 이름 추출
            parsed_url = urlparse(url)
            site_name = parsed_url.netloc
            
            new_policy = PrivacyPolicy.objects.create(
                user=request.user,
                url=url,
                site_name=site_name,
                summary="generated summary"  # 요약 생성 로직 추가
            )
            
            return redirect('summary_detail', pk=new_policy.pk)
        else:
            print("폼 오류:", form.errors)
    else:
        form = SummaryForm()
     
    return render(request, 'home.html', {'form': form})

def summary_detail(request, pk):
    summary = get_object_or_404(PrivacyPolicy, pk=pk, user=request.user)
    return render(request, 'summary_detail.html', {'summary': summary})

def history(request):
  if not request.user.is_authenticated:
        return redirect('login')
    
  summaries = PrivacyPolicy.objects.filter(user=request.user).order_by('summary_date')
  return render(request, 'history.html', {'summaries': summaries, 'user': request.user})

def delete_policy(request):
    if request.method == 'POST':
        PrivacyPolicy.objects.filter(user=request.user).delete() # 모든 PrivacyPolicy 객체 삭제
        return redirect('history')  # 삭제 후 'history' 페이지로 리다이렉트
    return redirect('history')  # POST 요청이 아닌 경우에도 'history' 페이지로 리다이렉트