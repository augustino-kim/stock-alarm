import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
import time

# ⚠️ 발급받으신 토큰과 챗ID
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
    # [1] 투자자별 매매동향 (금융투자 포함)
    # ==========================================
    msg1 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[1] 투자자별 매매동향 (단위: 억)\n"
    markets_investor = {"코스피": "", "코스닥": "02", "선물": "03"}
    
    for name, sosok in markets_investor.items():
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
                if len(cols) >= 5 and ":" in cols[0].text:
                    time_str = cols[0].text.strip()
                    retail = cols[1].text.strip()
                    foreigner = cols[2].text.strip()
                    inst = cols[3].text.strip()
                    financial = cols[4].text.strip()
                    
                    msg1 += f"{time_str} | {retail} | {foreigner} | {inst} | {financial}\n"
                    found = True
            if not found: break
            page += 1
        msg1 += "--------------------\n"

    send_telegram_msg(msg1)
    time.sleep(1)

    # ==========================================
    # [2] 지수 시간별 흐름 (거짓 데이터 필터링)
    # ==========================================
    msg2 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[2] 지수 시간별 흐름\n"
    markets_index = {"KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ"}
    
    for name, code in markets_index.items():
        msg2 += f"\n▶ {name}\n체결시각 | 체결가 | 거래대금(십억)\n"
        page = 1
        while page <= 4:
            url = f"https://finance.naver.com/sise/sise_index_time.naver?code={code}&thistime={thistime}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            found = False
            for row in rows:
                cols = row.find_all('td')
                
                # 거래대금 데이터가 있는 6번째 열(cols[5])까지 안전하게 확인
                if len(cols) >= 6 and cols[0].text.strip() and ":" in cols[0].text:
                    time_str = cols[0].text.strip()
                    price = cols[1].text.strip()
                    amount_raw = cols[5].text.strip()
                    
                    # 💡 핵심: 거래대금이 '-' 이거나 비어있으면 건너뛰기 (continue)
                    if amount_raw == "-" or not amount_raw:
                        continue
                        
                    # 거래대금(백만 단위)을 가져와 십억 단위로 계산 후 쉼표 처리
                    try:
                        amount_num = int(amount_raw.replace(',', ''))
                        amount_billion = amount_num // 1000
                        amount_str = f"{amount_billion:,}"
                    except ValueError:
                        amount_str = amount_raw # 혹시 모를 오류 시 원본 출력
                    
                    msg2 += f"{time_str} | {price} | {amount_str}\n"
                    found = True
            if not found: break
            page += 1
        msg2 += "--------------------\n"

    # ==========================================
    # [추가] 글로벌 에너지 가격 (인베스팅닷컴)
    # ==========================================
    msg2 += "\n▶ 글로벌 에너지 가격\n"
    
    # 💡 세 개의 사이트와 이름을 리스트로 묶어서 차례대로 실행합니다.
    investing_targets = [
        ("Brent Oil Futures (브렌트유 선물)", "https://www.investing.com/commodities/brent-oil"),
        ("Crude Oil Futures (크루드 오일 선물)", "https://www.investing.com/commodities/crude-oil"),
        ("WTI/USD present (서부텍사스유 현물)", "https://www.investing.com/currencies/wti-usd")
    ]
    
    headers_inv = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    for name, url_inv in investing_targets:
        try:
            res_inv = requests.get(url_inv, headers=headers_inv, timeout=10)
            if res_inv.status_code == 200:
                soup_inv = BeautifulSoup(res_inv.text, 'html.parser')
                # 3개 사이트 모두 공통적으로 사용하는 data-test 속성을 찾아 값을 추출합니다.
                price_div = soup_inv.find('div', {'data-test': 'instrument-price-last'})
                
                if price_div:
                    price_val = price_div.text.strip()
                    msg2 += f"{name} | $ {price_val}\n"
                else:
                    msg2 += f"{name} | 데이터 파싱 실패\n"
            else:
                msg2 += f"{name} | 접근 차단 ({res_inv.
