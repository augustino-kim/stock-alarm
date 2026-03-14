import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys

# 따옴표 안에 본인의 정보가 정확히 들어갔는지 빈칸이나 줄바꿈은 없는지 꼭 확인하세요!
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    print("텔레그램 전송을 시도합니다...")
    for i in range(0, len(text), 4000):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        res = requests.get(url, params={'chat_id': CHAT_ID, 'text': text[i:i+4000]})
        
        # 전송에 실패하면 이유를 뱉고 즉시 에러(빨간불)를 발생시킵니다!
        if res.status_code != 200:
            print(f"❌ 텔레그램 전송 실패! 상세 에러: {res.text}")
            sys.exit(1) # 강제 종료
        else:
            print("✅ 텔레그램 전송 성공!")

def get_market_data():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    # 주말이므로 어제(금요일) 데이터 강제 조회
    bizdate = '20260313' 
    
    markets = {"코스피": "", "코스닥": "02", "선물": "03"}
    full_msg = f"📊 [테스트: 2026-03-13 기준 매매동향]\n"
    
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
                    full_msg += f"{cols[0].text.strip()} | {cols[1].text.strip()} | {cols[2].text.strip()} | {cols[3].text.strip()}\n"
                    found_on_this_page = True
                    data_found = True
                    
            if not found_on_this_page or page >= 3: 
                break
            page += 1
            
        if not data_found:
            full_msg += "데이터가 없습니다.\n"
            
        full_msg += "--------------------\n"
        
    send_telegram_msg(full_msg)

if __name__ == "__main__":
    get_market_data()
