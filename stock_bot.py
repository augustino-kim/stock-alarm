import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
import time

# ⚠️ 토큰과 챗ID
TOKEN = '8680111639:AAEEJW7LFqYRCPub3MyJ9OrBR8gHT3MkaK4'
CHAT_ID = '696237698'

def send_telegram_msg(text):
    print("텔레그램 전송 시도 중...")
    for i in range(0, len(text), 4000):
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        res = requests.get(url, params={'chat_id': CHAT_ID, 'text': text[i:i+4000]})
        if res.status_code != 200:
            print(f"❌ 전송 실패: {res.text}")
            sys.exit(1)

def get_all_market_data():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    bizdate = now_kst.strftime('%Y%m%d')
    thistime = now_kst.strftime('%Y%m%d%H%M%S')
    
    # [1] 투자자별 매매동향
    msg1 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[1] 투자자별 매매동향 (단위: 억)\n"
    markets_investor = {"코스피": "", "코스닥": "02", "선물": "03"}
    
    for name, sosok in markets_investor.items():
        msg1 += f"\n▶ {name}\n시간 | 개인 | 외국인 | 기관 | 금투\n"
        url = f"https://finance.naver.com/sise/investorDealTrendTime.naver?bizdate={bizdate}&sosok={sosok}&page=1"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5 and ":" in cols[0].text:
                msg1 += f"{cols[0].text.strip()} | {cols[1].text.strip()} | {cols[2].text.strip()} | {cols[3].text.strip()} | {cols[4].text.strip()}\n"
        msg1 += "--------------------\n"

    send_telegram_msg(msg1)
    time.sleep(1)

    # [2] 지수 및 유가 현황
    msg2 = f"🔔 [{now_kst.strftime('%Y-%m-%d %H:%M')}]\n[2] 지수 및 유가 현황\n"
    
    # 지수 크롤링 (KOSPI/KOSDAQ)
    markets_index = {"KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ"}
    for name, code in markets_index.items():
        msg2 += f"\n▶ {name}\n체결시각 | 체결가 | 거래대금(십억)\n"
        url = f"https://finance.naver.com/sise/sise_index_time.naver?code={code}&thistime={thistime}&page=1"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6 and ":" in cols[0].text:
                time_str, price, amount_raw = cols[0].text.strip(), cols[1].text.strip(), cols[5].text.strip()
                if amount_raw == "-": continue
                try:
                    amount_billion = int(amount_raw.replace(',', '')) // 1000
                    msg2 += f"{time_str} | {price} | {amount_billion:,}\n"
                except: pass
        msg2 += "--------------------\n"

    # 유가 크롤링 (네이버 금융 버전 - 선물 가격)
    msg2 += "\n▶ 국제 유가 선물 (네이버)\n"
    oil_targets = [
        ("WTI 선물", "OIL_CL"),
        ("브렌트유 선물", "OIL_BRT")
    ]
    
    for name, code in oil_targets:
        try:
            url_oil = f"https://finance.naver.com/marketindex/worldOilDetail.naver?marketindexCd={code}"
            res_oil = requests.get(url_oil, headers={'User-Agent': 'Mozilla/5.0'})
            soup_oil = BeautifulSoup(res_oil.text, 'html.parser')
            # 네이버 금융 유가 페이지의 현재가 위치 추출
            price_tag = soup_oil.find('em', {'class': 'no_up'}) or soup_oil.find('em', {'class': 'no_down'}) or soup_oil.find('em', {'class': 'no_steady'})
            if price_tag:
                price_val = price_tag.find('span', {'class': 'blind'}).text
                msg2 += f"{name} | $ {price_val}\n"
            else:
                msg2 += f"{name} | 가격 추출 실패\n"
        except:
            msg2 += f"{name} | 통신 오류\n"
    
    msg2 += "--------------------\n"
    send_telegram_msg(msg2)

if __name__ == "__main__":
    get_all_market_data()
