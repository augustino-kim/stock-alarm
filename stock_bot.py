import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys

# ⚠️ 여기에 발급받으신 토큰과 챗ID를 다시 꼭 넣어주세요!
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    print("텔레그램 전송 시도 중...")
    # 텔레그램 글자 수 제한(4096자)을 넘지 않도록 4000자 단위로 쪼개서 안전하게 전송합니다.
    for i in range(0, len(text), 4000):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        res = requests.get(url, params={'chat_id': CHAT_ID, 'text': text[i:i+4000]})
        
        if res.status_code != 200:
            print(f"❌ 텔레그램 전송 실패! 상세 에러: {res.text}")
            sys.exit(1)

def get_all_market_data():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    bizdate = now_kst.strftime('%Y%m%d')
    thistime = now_kst.strftime('%Y%m%d%H%M%S')
    
    # 텔레그램 메시지 시작 부분
    full_msg = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')} 시장 종합 브리핑]\n"
    
    # ==========================================
    # 1. 투자자별 시간별 매매동향 (수급)
    # ==========================================
    full_msg += "\n[1] 투자자별 매매동향 (단위: 억)\n"
    markets_investor = {"코스피": "", "코스닥": "02", "선물": "03"}
    
    for name, sosok in markets_investor.items():
        full_msg += f"\n▶ {name}\n시간 | 개인 | 외국인 | 기관계\n"
        page = 1
        while page <= 3: # 매매동향은 기존대로 3페이지 수집
            url = f"https://finance.naver.com/sise/investorDealTrendTime.naver?bizdate={bizdate}&sosok={sosok}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            found = False
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4 and ":" in cols[0].text:
                    full_msg += f"{cols[0].text.strip()} | {cols[1].text.strip()} | {cols[2].text.strip()} | {cols[3].text.strip()}\n"
                    found = True
            if not found: break
            page += 1
        full_msg += "--------------------\n"

    # ==========================================
    # 2. 시간별 지수 흐름 (수정된 부분)
    # ==========================================
    full_msg += "\n[2] 지수 시간별 흐름\n"
    markets_index = {"KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ"}
    
    for name, code in markets_index.items():
        # 출력 열을 체결시각과 체결가로 단순화
        full_msg += f"\n▶ {name}\n체결시각 | 체결가\n"
        page = 1
        while page <= 4: # 수집 분량을 4페이지로 증가
            url = f"https://finance.naver.com/sise/sise_index_time.naver?code={code}&thistime={thistime}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            found = False
            for row in rows:
                cols = row.find_all('td')
                # 데이터가 존재하는 실제 행만 추출
                if len(cols) >= 4 and cols[0].text.strip() and ":" in cols[0].text:
                    time_str = cols[0].text.strip()
                    price = cols[1].text.strip()
                    
                    # 원하는 두 개의 데이터만 메시지에 추가
                    full_msg += f"{time_str} | {price}\n"
                    found = True
            if not found: break
            page += 1
        full_msg += "--------------------\n"

    # 최종 조립된 메시지 발송
    send_telegram_msg(full_msg)

if __name__ == "__main__":
    get_all_market_data()
