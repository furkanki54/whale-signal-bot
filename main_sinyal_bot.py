import requests
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from coin_list import coin_list

def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=6"
    try:
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and len(data) == 6:
            return data
        return None
    except Exception as e:
        print(f"HATA: {symbol} verisi çekilemedi → {e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram mesaj hatası → {e}")

def analyze_coin(symbol):
    data = get_binance_data(symbol)
    if not data:
        return

    try:
        # Son 5 mumdan hacim ortalaması al
        volumes = [float(k[5]) for k in data[:-1]]
        avg_volume = sum(volumes) / len(volumes)
        last_volume = float(data[-1][5])
        volume_change = ((last_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0

        # Fiyat değişimi: son mum open/close
        open_price = float(data[-1][1])
        close_price = float(data[-1][4])
        price_change = ((close_price - open_price) / open_price) * 100

        if volume_change >= 30 and abs(price_change) >= 3:
            direction = "📈 YÜKSELİŞ" if price_change > 0 else "📉 DÜŞÜŞ"
            message = (
                f"🚨 *Sinyal Tespit Edildi!*\n\n"
                f"🪙 Coin: `{symbol}`\n"
                f"💰 Fiyat: {close_price:.4f} USDT\n"
                f"📊 Fiyat Değişimi: %{price_change:.2f}\n"
                f"📈 Hacim Artışı: %{volume_change:.2f}\n"
                f"{direction} 🐋 Balina Aktivitesi!"
            )
            send_telegram_message(message)

    except Exception as e:
        print(f"{symbol} işlenirken hata: {e}")

def main():
    while True:
        for symbol in coin_list:
            if symbol.endswith("USDT"):
                analyze_coin(symbol)
            time.sleep(0.2)
        print("✅ 5 dakikalık analiz tamamlandı. Bekleniyor...")
        time.sleep(300)

if __name__ == "__main__":
    main()
