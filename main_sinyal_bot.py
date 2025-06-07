import requests
import pandas as pd
import time
from telebot import TeleBot
from config import TOKEN, CHAT_ID, VOLUME_THRESHOLD, PRICE_THRESHOLD

bot = TeleBot(TOKEN)

# Coin listesini oku
def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f.readlines()]

# Binance API'den son 2 mumu çek
def get_ohlcv(symbol, interval="1h", limit=2):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

# Sinyal üret
def check_signal(symbol):
    df = get_ohlcv(symbol)
    if df is None or len(df) < 2:
        return None

    prev = df.iloc[-2]
    last = df.iloc[-1]

    price_change = ((last["close"] - prev["close"]) / prev["close"]) * 100
    volume_change = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    if volume_change >= VOLUME_THRESHOLD and abs(price_change) >= PRICE_THRESHOLD:
        direction = "📈 Fiyat YÜKSELDİ" if price_change > 0 else "📉 Fiyat DÜŞTÜ"
        return f"""
🐳 *BALİNA SİNYALİ* — {symbol}
{direction}
Fiyat Değişimi: %{round(price_change, 2)}
Hacim Değişimi: %{round(volume_change, 2)}
"""
    return None

# Ana döngü
def run():
    coin_list = load_coin_list()
    for symbol in coin_list:
        try:
            signal = check_signal(symbol)
            if signal:
                bot.send_message(chat_id=CHAT_ID, text=signal, parse_mode="Markdown")
        except Exception as e:
            print(f"{symbol} için hata: {e}")

if __name__ == "__main__":
    run()
