import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
import time

# ⚠️ 여기에 발급받으신 토큰과 챗ID를 다시 꼭 넣어주세요!
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    print("텔레그램 전송 시도 중...")
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
    
    # ==========================================
    # [첫 번째 메시지] 투자자별 매매동향 (금융투자 추가)
    # ==========================================
    msg1 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[1] 투자자별 매매동향 (단위: 억)\n"
    markets_investor = {"코스피": "", "코스닥": "02", "선물": "03"}
    
    for name, sosok in markets_investor.items():
        # 열 헤더에 '금투' 추가
        msg1 += f"\n▶ {name}\n시간 | 개인 | 외국인 | 기관 | 금투\n"
        page = 1
        while page <= 2: 
            url = f"https://finance.naver.com/sise/investorDealTrendTime.naver?bizdate={bizdate}&sosok={sosok}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            found = False
            for row in rows:
                cols = row.find_all('td')
                # 데이터가 존재하고, 금융투자(cols[4])까지 있는 행만 추출
                if len(cols) >= 5 and ":" in cols[0].text:
                    time_str = cols[0].text.strip()
                    retail = cols[1].text.strip()
                    foreigner = cols[2].text.strip()
                    inst = cols[3].text.strip()
                    financial = cols[4].text.strip() # 금융투자 추가
                    
                    msg1 += f"{time_str} | {retail} | {foreigner} | {inst} | {financial}\n"
                    found = True
            if not found: break
            page += 1
        msg1 += "--------------------\n"

    # 첫 번째 메시지 발송
    send_telegram_msg(msg1)
    
    # 텔레그램 서버에서 메시지 순서가 뒤바뀌는 것을 방지하기 위해 1초 대기
    time.sleep(1)

    # ==========================================
    # [두 번째 메시지] 시간별 지수 흐름 (기존 유지)
    # ==========================================
    msg2 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[2] 지수 시간별 흐름\n"
    markets_index = {"KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ"}
    
    for name, code in markets_index.items():
        msg2 += f"\n▶ {name}\n체결시각 | 체결가\n"
        page = 1
        while page <= 4:
            url = f"https://finance.naver.com/sise/sise_index_time.naver?code={code}&thistime={thistime}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            found = False
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4 and cols[0].text.strip() and ":" in cols[0].text:
                    time_str = cols[0].text.strip()
                    price = cols[1].text.strip()
                    
                    msg2 += f"{time_str} | {price}\n"
                    found = True
            if not found: break
            page += 1
        msg2 += "--------------------\n"

    # 두 번째 메시지 발송
    send_telegram_msg(msg2)

if __name__ == "__main__":
    get_all_market_data()
