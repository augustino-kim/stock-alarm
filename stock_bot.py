import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys

# 따옴표 안에 본인의 정보로 다시 세팅해 주세요!
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    for i in range(0, len(text), 4000):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        res = requests.get(url, params={'chat_id': CHAT_ID, 'text': text[i:i+4000]})
        
        if res.status_code != 200:
            print(f"❌ 텔레그램 전송 실패! 상세 에러: {res.text}")
            sys.exit(1)

def get_market_data():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    
    # [핵심 변경] 강제 세팅했던 어제 날짜를 지우고, 코드가 실행되는 시점의 '오늘 날짜'를 자동으로 생성합니다.
    bizdate = now_kst.strftime('%Y%m%d') 
    
    markets = {"코스피": "", "코스닥": "02", "선물": "03"}
    full_msg = f"📊 [{now_kst.strftime('%Y-%m-%d %H:%M')} 기준 당일 매매동향]\n"
    
    for name, sosok in markets.items():
        full_msg += f"\n▶ {name}\n시간 | 개인 | 외국인 | 기관계\n"
        page = 1
        data_found = False
        
        while True:
            url = f"https://finance.naver.com/sise/investorDealTrendTime.naver?bizdate={bizdate}&sosok={sosok}&page={page}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            
            found_on_this_page = False
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4 and ":" in cols[0].text:
                    # 화면에 적힌 숫자 그대로를 어떠한 임의의 연산 없이 텍스트로 추출합니다.
                    time_str = cols[0].text.strip()
                    retail = cols[1].text.strip()
                    foreigner = cols[2].text.strip()
                    inst = cols[3].text.strip()
                    
                    full_msg += f"{time_str} | {retail} | {foreigner} | {inst}\n"
                    found_on_this_page = True
                    data_found = True
                    
            # 너무 많은 과거 데이터를 보내지 않도록 최대 3페이지(최근 약 30분 치)까지만 수집하고 끊습니다.
            if not found_on_this_page or page >= 3: 
                break
            page += 1
            
        # 장 시작 직후(09:00~09:02) 아직 데이터가 안 올라왔을 경우를 대비한 안내 문구
        if not data_found:
            full_msg += "현재 수집된 데이터가 없습니다.\n"
            
        full_msg += "--------------------\n"
        
    send_telegram_msg(full_msg)

if __name__ == "__main__":
    get_market_data()
