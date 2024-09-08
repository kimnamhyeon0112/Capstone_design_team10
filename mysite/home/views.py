from django.shortcuts import render, redirect, get_object_or_404
from .forms import SummaryForm
from users.models import PrivacyPolicy
from urllib.parse import urlparse
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import time

client = OpenAI(api_key='YOUR API KEY')  # OpenAI 클라이언트 설정

def get_terms_from_url(url):
    """URL에서 약관 텍스트 추출"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text(separator='\n', strip=True)
        return all_text
    except Exception as e:
        return f"오류 발생: {e}"

def summarize_part(part):
    """약관 텍스트의 각 부분을 요약"""
    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"다음 약관을 간단히 요약해 주세요: {part}"}]
            )
            return response.choices[0].message.content
        except Exception as e:
            if 'rate limit reached' in str(e):
                print("Rate limit reached. 대기 중...")
                time.sleep(2)
            else:
                raise
            
def summarize_terms(terms_text):
    """약관 텍스트를 분할하고 각각 요약"""
    max_length = 2000  # GPT 모델이 처리할 수 있는 최대 텍스트 길이 설정
    parts = [terms_text[i:i + max_length] for i in range(0, len(terms_text), max_length)]

    summaries = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(summarize_part, part) for part in parts]
        for future in futures:
            summaries.append(future.result())

    return "\n".join(summaries)

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

            terms_text = get_terms_from_url(url)
            
            if "오류 발생" not in terms_text:
                summary = summarize_terms(terms_text)
                
                new_policy = PrivacyPolicy.objects.create(
                    user=request.user,
                    url=url,
                    site_name=site_name,
                    summary=summary
                )
                
                return redirect('summary_detail', pk=new_policy.pk)
            
            else:
                return render(request, 'summary_detail.html', {'error': terms_text})   
            
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