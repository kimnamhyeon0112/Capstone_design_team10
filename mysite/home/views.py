from django.shortcuts import render, redirect, get_object_or_404
from .forms import SummaryForm
from users.models import PrivacyPolicy
from urllib.parse import urlparse
import requests
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

client = OpenAI(api_key='YOUR_API_KEY')  # OpenAI 클라이언트 설정

def get_terms_from_url(url):
    """URL에서 약관 텍스트 추출"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"오류 발생: {e}"

def summarize_part(part):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"다음 개인정보 처리 방침을 간단히 요약해 주세요. "
                        f"핵심 내용만 포함하고, 불필요한 정보는 제외해 주세요. "
                        f"'수집', '이용', '제공', '보관'과 같은 중요한 키워드에 중점을 두고 요약해 주세요.: {part}"
                    )
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None
            
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

def analyze_sentiment(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"다음 문장에서 개인정보 침해의 가능성에 대해 안전함 또는 주의 필요 또는 위험함으로 판단해 주세요: {text}"
                    )
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return None

def home(request):
    if request.method == 'POST':
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = SummaryForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            parsed_url = urlparse(url)
            site_name = parsed_url.netloc

            terms_text = get_terms_from_url(url)
            
            if "오류 발생" not in terms_text:
                summary = summarize_terms(terms_text)  # 약관 요약
                print("Summary:", summary)  # 요약 결과 확인
                
                if summary:  # 요약이 성공적으로 이루어진 경우
                    # 감성 분석 수행
                    sentiment_result = analyze_sentiment(summary)
                    print("Sentiment Result:", sentiment_result)  # 감성 분석 결과 확인
                    new_policy = PrivacyPolicy.objects.create(
                        user=request.user,
                        url=url,
                        site_name=site_name,
                        sentiment_result=sentiment_result,
                        summary=summary
                    )
                    # 신호등 결정 로직
                    if "안전함" in sentiment_result:
                        traffic_light = 'green_light.png'  # 초록색 신호등
                    elif "주의 필요" in sentiment_result:
                        traffic_light = 'yellow_light.png'  # 노란색 신호등
                    elif "위험함" in sentiment_result:
                        traffic_light = 'red_light.png'  # 빨간색 신호등
                    else:
                        traffic_light = 'default_light.png'  # 기본 신호등 (예: 회색)
                        
                    return render(request, 'summary_detail.html', {
                        'summary': new_policy,
                        'sentiment_result': sentiment_result,  # 감성 분석 결과 전달
                        'traffic_light': traffic_light,  # 트래픽 라이트 이미지 경로
                    })

            
            else:
                return render(request, 'summary_detail.html', {'error': '요약 결과가 없습니다.'})
            
        else:
            print("폼 오류:", form.errors)
    else:
        form = SummaryForm()
     
    return render(request, 'home.html', {'form': form})

def summary_detail(request, pk):
    # 개인정보 처리방침을 가져옵니다 (summary)
    summary = get_object_or_404(PrivacyPolicy, pk=pk, user=request.user)
    
    summary.update_visit()  # 방문 시간 업데이트
    
    sentiment_result = summary.sentiment_result  # 감성 분석 결과
    
    # sentiment_result가 None이 아닌 경우에만 로직을 수행
    if sentiment_result:
        if "안전함" in sentiment_result:
            traffic_light = 'green_light.png'
        elif "주의 필요" in sentiment_result:
            traffic_light = 'yellow_light.png'
        elif "위험함" in sentiment_result:
            traffic_light = 'red_light.png'
        else:
            traffic_light = 'default_light.png'
    else:
        traffic_light = 'default_light.png'  # sentiment_result가 없을 경우 기본값 설정
    
    # 템플릿에 데이터를 전달
    return render(request, 'summary_detail.html', {
        'summary': summary,
        'traffic_light': traffic_light,
        'sentiment_result': sentiment_result
    })


def history(request):
  if not request.user.is_authenticated:
        return redirect('login')
    
  show_checked_only = request.GET.get('show_checked_only', 'false') == 'true'
  show_unchecked_only = request.GET.get('show_unchecked_only', 'false') == 'true'
  
  # 중복을 제거한 최신 항목 가져오기
  latest_entries = PrivacyPolicy.objects.filter(user=request.user).order_by('url', '-summary_date').distinct('url')
  
  if show_checked_only:
        summaries = latest_entries.filter(is_checked=True)   # 가입한 사이트만 표시
  elif show_unchecked_only:
        summaries = latest_entries.filter(is_checked=False)  # 가입하지 않은 사이트만 표시
  else:
        summaries = latest_entries  # 모든 항목 표시      
        
  return render(request, 'history.html', {'summaries': summaries, 'user': request.user, 'show_checked_only': show_checked_only, 'show_unchecked_only': show_unchecked_only})

def delete_policy(request):
    if request.method == 'POST':
        PrivacyPolicy.objects.filter(user=request.user).delete() # 모든 PrivacyPolicy 객체 삭제
        return redirect('history')  # 삭제 후 'history' 페이지로 리다이렉트
    return redirect('history')  # POST 요청이 아닌 경우에도 'history' 페이지로 리다이렉트

def update_check_status(request):
    if request.method == 'POST':
        # 체크된 항목의 ID를 가져옴
        checked_ids = request.POST.getlist('checked_ids')

        # 모든 항목의 is_checked 상태를 False로 초기화
        PrivacyPolicy.objects.filter(user=request.user).update(is_checked=False)

        # 체크된 항목은 is_checked를 True로 설정
        PrivacyPolicy.objects.filter(pk__in=checked_ids, user=request.user).update(is_checked=True)

    return redirect('history')  # 완료 후 'history' 페이지로 리다이렉트
       

