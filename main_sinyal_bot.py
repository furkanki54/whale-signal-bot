import requests
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from coin_list import coin_list

def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=2"
    try:
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and len(data) == 2:
            return data
        return None
    except Exception as e:
        print(f"Hata: {symbol} veri çekilemedi -> {e}")
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
        print(f"Telegram'a mesaj gönderilemedi -> {e}")

def analyze_coin(symbol):
    data = get_binance_data(symbol)
    if not data:
        return

    try:
        prev = data[0]
        curr = data[1]

        prev_close = float(prev[4])
        curr_close = float(curr[4])
        prev_volume = float(prev[5])
        curr_volume = float(curr[5])

        if prev_volume == 0:
            return

        price_change = ((curr_close - prev_close) / prev_close) * 100
        volume_change = ((curr_volume - prev_volume) / prev_volume) * 100

        if abs(price_change) >= 3 and volume_change >= 30:
            direction = "📈 YÜKSELİŞ" if price_change > 0 else "📉 DÜŞÜŞ"
            message = (
                f"🚨 *Sinyal Tespit Edildi!*\n\n"
                f"🪙 Coin: `{symbol}`\n"
                f"💰 Fiyat: {curr_close:.4f} USDT\n"
                f"📊 Fiyat Değişimi: %{price_change:.2f}\n"
                f"📈 Hacim Değişimi: %{volume_change:.2f}\n"
                f"{direction} 🐋 Balina Aktivitesi!"
            )
            send_telegram_message(message)

    except Exception as e:
        print(f"Hata oluştu: {symbol} – {str(e)}")

def main():
    while True:
        for symbol in coin_list:
            if symbol.endswith("USDT"):
                analyze_coin(symbol)
            time.sleep(0.2)  # Binance rate limit için yavaşlat
        time.sleep(3600)  # Her saat başı tekrar çalış

if __name__ == "__main__":
    main()
