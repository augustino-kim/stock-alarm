import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 본인의 정보로 수정
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    for i in range(0, len(text), 4000):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={'chat_id': CHAT_ID, 'text': text[i:i+4000]})

def get_market_data():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    bizdate = now_kst.strftime('%Y%m%d') 
    markets = {"코스피": "", "코스닥": "02", "선물": "03"}
    full_msg = f"📊 [{now_kst.strftime('%Y-%m-%d %H:%M')} 기준 당일 매매동향]\n"
    
    for name, sosok in markets.items():
        full_msg += f"\n▶ {name}\n시간 | 개인 | 외국인 | 기관계\n"
        page = 1
        while True:
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
            if not found or page >= 3: break # 너무 길어지지 않게 최대 3페이지까지만
            page += 1
        full_msg += "--------------------\n"
    send_telegram_msg(full_msg)

if __name__ == "__main__":
    get_market_data()
