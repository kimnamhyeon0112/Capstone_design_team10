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

client = OpenAI(api_key='YOUR_API_KEY')  # OpenAI 클라이언트 설정

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
                messages=[{"role": "user", "content": f"다음 개인정보 처리 방침을 간단히 요약해 주세요. 핵심 내용만 포함하고, 불필요한 정보는 제외해 주세요. '수집', '이용', '제공', '보관'과 같은 중요한 키워드에 중점을 두고 요약해 주세요.: {part}"}]
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

def highlight_keywords(text):
    keywords = [
        "이용자 동의 없이",
        "사용자 동의 없이",
        "개인정보를 수집",
        "국외 이전",
        "해외 이전",
        "자동 수집",
        "법령",
        "회원탈퇴 시",
        "회원 탈퇴시",
        "회원 탈퇴 시",
        "동의 철회",
        "파기 절차",
        "파기절차",
        "파기 방법",
        "파기방법",
        "마케팅 활용",
        "개인정보 변경",
        "파기 절차",
        "법적 요건",
        "익명 처리",
        "위치 정보",
        "개인정보 보호 책임자",
        "변경 고지",
        "수집 목적",        
        "관련 법령에 의해 보존",
        "법령에서 정한 기간",
        "보안",
        "최소한의 개인정보를 수집",
        "동의",
        "법령에 따라",
        "회원탈퇴",
        "회원 탈퇴",
        "보유 및 이용기간 경과",
        "내부 규정",
        "내부규정",
        "파기 절차",
        "다른 용도로 활용되지 않으며",
        "필요한 경우에만 규정된 범위 내",
        "이용자의 정보는 안전하게 보관",
        "동의 없이 제 3자에게 제공되지 않습니다",
        "동의 없이 제 3자에게 제공되지 않음",
        "동의 없이 제 3자에게 제공되지 않는다.",
        "개인정보 보호",
        "엄격한 교육",
        "감독을 통해",
        "이용자 정보 관련 분쟁 발생 시 적극 대응 및 문의 가능",
        "암호화",
        "제3자에게 제공되지 않음",
        "안전 조치",
        "일정 기간",
        "개인정보 보관",
        "개인정보의 파기",
        "정보 보관이 요구될 경우",
        "해당 기간 동안",
        "개인정보 안전하게 보관 후 파기",
        "개인정보를 안전하게 보관한 후 파기",
        "원칙적으로 개인정보의 수집 및 이용 목적이 달성",
        "목적 달성 후",
        "목적이 달성",
        "즉시 파기",
        "보유 및 이용 기간이 종료",
        "지체없이 파기",
        "법령에 따라 제공되는 경우를 제외",
        # 추가적인 키워드...
    ]
    
    highlighted_count = 0
    for keyword in keywords:
        occurrences = text.count(keyword) 
        if occurrences > 0:
            highlighted_count += occurrences
            text = text.replace(keyword, f"<span class='highlight'>{keyword}</span>")

    return text, highlighted_count

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
                
                highlighted_summary, highlighted_count = highlight_keywords(summary)  # 키워드 강조
                if highlighted_count > 10:
                    traffic_light = 'green_light.png'
                elif 6 <= highlighted_count <= 9:
                    traffic_light = 'yellow_light.png'
                else:
                    traffic_light = 'red_light.png'
                    
                return render(request, 'summary_detail.html', {
                    'summary': new_policy,
                    'highlighted_summary': highlighted_summary,
                    'traffic_light': traffic_light,
                    'highlighted_count': highlighted_count
                    })

            
            else:
                return render(request, 'summary_detail.html', {'error': terms_text})   
            
        else:
            print("폼 오류:", form.errors)
    else:
        form = SummaryForm()
     
    return render(request, 'home.html', {'form': form})

def summary_detail(request, pk):
    # 개인정보 처리방침을 가져옵니다 (summary)
    summary = get_object_or_404(PrivacyPolicy, pk=pk, user=request.user)
    
    summary.update_visit()  # 방문 시간 업데이트
    
    highlighted_summary, highlighted_count = highlight_keywords(summary.summary)
    
    # 트래픽 라이트 이미지 경로 설정
    if highlighted_count > 10:
        traffic_light = 'green_light.png'
    elif 6 <= highlighted_count <= 9:
        traffic_light = 'yellow_light.png'
    else:
        traffic_light = 'red_light.png'
    
    # 템플릿에 데이터를 전달
    return render(request, 'summary_detail.html', {
        'summary': summary,
        'highlighted_summary': highlighted_summary,
        'traffic_light': traffic_light,
        'highlighted_count': highlighted_count
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
       

