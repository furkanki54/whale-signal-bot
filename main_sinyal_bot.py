import requests
import time
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from coin_list import coin_list
import math

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=2"
    response = requests.get(url)
    data = response.json()
    return data

def analyze():
    for symbol in coin_list:
        try:
            data = fetch_binance_data(symbol)
            if len(data) < 2:
                continue

            previous_candle = data[0]
            current_candle = data[1]

            previous_volume = float(previous_candle[5])
            current_volume = float(current_candle[5])
            current_price = float(current_candle[4])
            open_price = float(current_candle[1])

            if previous_volume == 0:
                continue

            volume_change = ((current_volume - previous_volume) / previous_volume) * 100
            price_change = ((current_price - open_price) / open_price) * 100

            if volume_change >= 30 and abs(price_change) >= 3:
                direction = "ð YÃ¼kseliÅ" if price_change > 0 else "ð DÃ¼ÅÃ¼Å"
                message = f"ð¨ Sinyal: {symbol}\nFiyat: {current_price:.4f} USDT\nFiyat DeÄiÅimi: %{price_change:.2f}\nHacim DeÄiÅimi: %{volume_change:.2f}\n{direction} ð Balina Aktivitesi!"
                send_telegram_message(message)

        except Exception as e:
            print(f"Hata oluÅtu: {symbol} - {str(e)}")

while True:
    analyze()
    time.sleep(3600)
