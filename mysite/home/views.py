from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import time

def home(request):
    return render(request, 'home.html', {})

# OpenAI 클라이언트 설정
client = OpenAI(api_key='YOUR API KEY')

def get_terms_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text(separator='\n', strip=True)
        return all_text
    except Exception as e:
        return f"오류 발생: {e}"

def summarize_part(part):
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
    max_length = 2000
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
        "제3자 제공",
        "외국에 제공",
        "국외 이전"
        "제공",
        "이용",
        "보관",
        "수집",
        "해외 이전",
        "자동 수집",
        "쿠키",
        "보관 기간",
        "삭제 요청 무시",
        "처리 위탁",
        "위탁 업체",
        "마케팅 활용",
        "개인정보 변경",
        "정보 공유",
        "비밀번호 저장",
        "파기 절차",
        "법적 요건",
        "불법 수집",
        "민감한 정보",
        "익명 처리",
        "동의 없이",
        "위치 정보",
        "유효하지 않은 정보",
        "책임 회피",
        "기술적 조치 미비",
        "개인정보 보호 책임자",
        "교육 미비",
        "정보 유출",
        "변경 고지",
        "목적 불분명",
        "수집 목적",
        # 추가적인 키워드...
    ]
    
    highlighted_count = 0
    for keyword in keywords:
        occurrences = text.count(keyword) 
        if occurrences > 0:
            highlighted_count += occurrences
            text = text.replace(keyword, f"<span class='highlight'>{keyword}</span>")

    return text, highlighted_count


def summary(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        terms_text = get_terms_from_url(url)

        if "오류" not in terms_text:
            summary = summarize_terms(terms_text)
            summary, highlighted_count = highlight_keywords(summary)  # 키워드 강조
            if highlighted_count > 30:
                traffic_light = 'red_light.png'
            elif 10 <= highlighted_count <= 30:
                traffic_light = 'yellow_light.png'
            else:
                traffic_light = 'green_light.png'
            return render(request, 'summary.html', {'summary': summary, 'traffic_light': traffic_light, 'highlighted_count': highlighted_count})
        else:
            return render(request, 'summary.html', {'error': terms_text})
    
    return render(request, 'summary.html')
# Create your views here.