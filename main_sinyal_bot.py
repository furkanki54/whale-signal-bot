import requests
import time
from datetime import datetime
from telebot import TeleBot

# Telegram Ayarları
TELEGRAM_TOKEN = "7724826009:AAF_WF8Uij2_LecA19I3oQ9b06YsGAQGovE"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

# Coin listesi
def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f.readlines()]

coin_list = load_coin_list()

# Önceki fiyatları tut
last_prices = {}

# Sinyal gönder
def send_signal(title, symbol, old_price, new_price, extra_note=""):
    pct_change = ((new_price - old_price) / old_price) * 100
    now = datetime.now().strftime("%H:%M:%S")
    msg = f"""
{title}
Coin: {symbol}
Fiyat: {old_price:.4f} → {new_price:.4f} (+{pct_change:.2f}%)
Zaman: {now}

{extra_note}
"""
    bot.send_message(CHAT_ID, msg.strip())

# Binance fiyat çek
def fetch_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    try:
        r = requests.get(url, timeout=5)
        return float(r.json()['price'])
    except:
        return None

# Binance 5m mum verisi çek (balina sinyali için)
def fetch_candles(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=5m&limit=2"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        prev = data[0]
        last = data[1]
        return {
            "prev_close": float(prev[4]),
            "last_close": float(last[4]),
            "prev_volume": float(prev[5]),
            "last_volume": float(last[5])
        }
    except:
        return None

# Ana döngü
while True:
    for symbol in coin_list:
        price = fetch_price(symbol)
        if not price:
            continue

        # Anlık fiyat artışı kontrolü
        if symbol in last_prices:
            old_price = last_prices[symbol]
            price_change = ((price - old_price) / old_price) * 100
            if price_change >= 1.80:
                send_signal("🚀 Anlık Yükseliş Tespit Edildi!", symbol, old_price, price, "📈 Hızlı pump olabilir!")

        last_prices[symbol] = price

        # Balina sinyali kontrolü (5 dakikalık mum)
        candle = fetch_candles(symbol)
        if candle:
            fiyat_degisim = ((candle["last_close"] - candle["prev_close"]) / candle["prev_close"]) * 100
            hacim_degisim = ((candle["last_volume"] - candle["prev_volume"]) / candle["prev_volume"]) * 100
            if fiyat_degisim >= 5 and hacim_degisim >= 30:
                send_signal("🐋 Balina Sinyali Tespit Edildi!", symbol, candle["prev_close"], candle["last_close"],
                            f"💰 Hacim: %{hacim_degisim:.2f} | Fiyat: %{fiyat_degisim:.2f}")

    time.sleep(10)  # Her 10 saniyede bir tüm coinler taranır
