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
    max_length = 2000
    parts = [terms_text[i:i + max_length] for i in range(0, len(terms_text), max_length)]
    
    summaries = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(summarize_part, part) for part in parts]
        for future in futures:
            summaries.append(future.result())

    return "\n".join(summaries)

def summary(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        terms_text = get_terms_from_url(url)

        if "오류" not in terms_text:
            summary = summarize_terms(terms_text)
            return render(request, 'summary.html', {'summary': summary})
        else:
            return render(request, 'summary.html', {'error': terms_text})
    
    return render(request, 'summary.html')
# Create your views here.