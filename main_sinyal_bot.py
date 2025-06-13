import time
import requests
import pandas as pd
from datetime import datetime
from telebot import TeleBot

# Telegram ayarları
TELEGRAM_TOKEN = "7724826009:AAF_WF8Uij2_LecA19I3oQ9b06YsGAQGovE"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

# Coin listesi
def load_coin_list():
    with open("coin_list.txt", "r") as file:
        return [line.strip().upper() for line in file]

coin_list = load_coin_list()

# Sinyal gönderme
def send_signal(message):
    bot.send_message(CHAT_ID, message)

# Coin verilerini çekme
def fetch_binance_data(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=5m&limit=2"
    response = requests.get(url)
    data = response.json()
    if not data or len(data) < 2:
        return None
    prev = data[0]
    last = data[1]
    try:
        prev_close = float(prev[4])
        last_close = float(last[4])
        prev_vol = float(prev[5])
        last_vol = float(last[5])
        price_change = ((last_close - prev_close) / prev_close) * 100
        vol_change = ((last_vol - prev_vol) / prev_vol) * 100
        return price_change, vol_change, last_close
    except:
        return None

# Ana döngü
def run():
    while True:
        for coin in coin_list:
            result = fetch_binance_data(coin)
            if result:
                price_change, vol_change, price = result
                if abs(price_change) >= 5 and abs(vol_change) >= 30:
                    direction = "📈 Fiyat YÜKSELDİ" if price_change > 0 else "📉 Fiyat DÜŞTÜ"
                    message = f"""
🚨 Sinyal Tespit Edildi 🚨
Coin: {coin}
Fiyat: {price:.2f} USDT
{direction}
Hacim Değişimi: %{vol_change:.2f}
Zaman: {datetime.now().strftime('%H:%M:%S')}
"""
                    send_signal(message)

        time.sleep(300)  # 5 dakika bekle

if __name__ == "__main__":
    run()
