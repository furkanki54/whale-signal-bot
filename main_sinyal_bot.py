import requests
import time
import pandas as pd
from datetime import datetime
import telebot

# ✅ Yeni token burada
TELEGRAM_TOKEN = "7724826009:AAF_WF8Uij2_LecA19I3oQ9b06YsGAQGovE"
CHAT_ID = "-1002549376225"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Coin listesi dosyadan alınır
def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f.readlines()]

# Binance API'den veri çekme
def get_klines(symbol, interval="5m", limit=2):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    return []

# Sinyal üret
def check_signal(symbol):
    data = get_klines(symbol)
    if len(data) < 2:
        return None

    prev = data[-2]
    last = data[-1]

    prev_vol = float(prev[5])
    last_vol = float(last[5])
    prev_close = float(prev[4])
    last_close = float(last[4])

    volume_change = ((last_vol - prev_vol) / prev_vol) * 100
    price_change = ((last_close - prev_close) / prev_close) * 100

    if volume_change > 30 and price_change > 5:
        return f"🚨 BALİNA ALIMI: {symbol}\n📈 Hacim: %{volume_change:.2f} | Fiyat: %{price_change:.2f}"
    elif volume_change > 30 and price_change < -5:
        return f"🚨 BALİNA SATIŞI: {symbol}\n📉 Hacim: %{volume_change:.2f} | Fiyat: %{price_change:.2f}"
    else:
        return None

# Sonsuz döngü
def run():
    coin_list = load_coin_list()
    while True:
        print(f"🔁 Yeni tarama: {datetime.now()}")
        sinyal_sayısı = 0
        for coin in coin_list:
            try:
                sinyal = check_signal(coin)
                if sinyal:
                    bot.send_message(CHAT_ID, sinyal)
                    sinyal_sayısı += 1
                    time.sleep(1)
            except Exception as e:
                print(f"Hata: {coin} - {str(e)}")
        if sinyal_sayısı == 0:
            bot.send_message(CHAT_ID, f"✅ {datetime.now().strftime('%H:%M')} - Tarama yapıldı, sinyale rastlanmadı.")
        time.sleep(300)  # 5 dakika

if __name__ == "__main__":
    run()
