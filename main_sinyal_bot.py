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
    try:
        with open("coin_list.txt", "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except Exception as e:
        print(f"[HATA] Coin listesi yüklenemedi: {e}")
        return []

coin_list = load_coin_list()

# Önceki fiyatları tut
last_prices = {}

# Sinyal gönder
def send_signal(title, symbol, old_price, new_price, extra_note=""):
    pct_change = ((new_price - old_price) / old_price) * 100
    now = datetime.now().strftime("%H:%M:%S")
    msg = f"""📡 {title}
🪙 Coin: {symbol}
💰 Fiyat: {old_price:.4f} → {new_price:.4f}  (%{pct_change:.2f})
⏰ Zaman: {now}
{extra_note}
"""
    try:
        bot.send_message(CHAT_ID, msg.strip())
        print(f"[SİNYAL GÖNDERİLDİ] {symbol} - {title}")
    except Exception as e:
        print(f"[TELEGRAM HATASI] {e}")

# Binance fiyat çek
def fetch_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    try:
        r = requests.get(url, timeout=5)
        return float(r.json()['price'])
    except Exception as e:
        print(f"[FİYAT HATASI] {symbol} - {e}")
        return None

# Binance 5m mum verisi çek (balina sinyali için)
def fetch_candles(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=5m&limit=2"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if len(data) < 2:
            return None
        prev = data[0]
        last = data[1]
        return {
            "prev_close": float(prev[4]),
            "last_close": float(last[4]),
            "prev_volume": float(prev[5]),
            "last_volume": float(last[5])
        }
    except Exception as e:
        print(f"[MUM VERİSİ HATASI] {symbol} - {e}")
        return None

# Ana döngü
while True:
    print(f"🔍 TARAMA BAŞLADI - {datetime.now().strftime('%H:%M:%S')}")
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
                            f"💰 Hacim Değişimi: %{hacim_degisim:.2f}\n📊 Fiyat Değişimi: %{fiyat_degisim:.2f}")

    print("⏳ 10 saniye sonra tekrar taranacak...\n")
    time.sleep(10)
