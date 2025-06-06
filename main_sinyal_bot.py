import time
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_BASE_URL
from coin_list import coin_list

def get_klines(symbol):
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 2
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

def analyze_coin(symbol):
    data = get_klines(symbol)
    if not data or len(data) < 2:
        return

    prev_kline = data[0]
    last_kline = data[1]

    try:
        prev_close = float(prev_kline[4])
        last_close = float(last_kline[4])
        prev_volume = float(prev_kline[5])
        last_volume = float(last_kline[5])

        price_change = ((last_close - prev_close) / prev_close) * 100
        volume_change = ((last_volume - prev_volume) / prev_volume) * 100 if prev_volume > 0 else 0

        if abs(price_change) >= 5 or volume_change >= 30:
            direction = "📈 Yükseliş" if price_change > 0 else "📉 Düşüş"
            whale = "🐋 Balina Aktivitesi!" if volume_change >= 30 else ""
            message = f"""
🚨 Sinyal: {symbol}
Fiyat: {last_close:.4f} USDT
Fiyat Değişimi: %{price_change:.2f}
Hacim Değişimi: %{volume_change:.2f}
{direction} {whale}
"""
            send_telegram_message(message)
    except Exception as e:
        print(f"Hata {symbol}: {e}")

def main():
    while True:
        for symbol in coin_list:
            if symbol.endswith("USDT"):
                analyze_coin(symbol)
            time.sleep(0.2)  # Binance rate limit'e takılmamak için
        time.sleep(300)  # 5 dakika bekle

if __name__ == "__main__":
    main()
