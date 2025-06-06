import requests
import pandas as pd
import numpy as np
from datetime import datetime
from telebot import TeleBot
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = TeleBot(TELEGRAM_TOKEN)

TIMEFRAMES = {
    "15m": "15 dakika",
    "1h": "1 saat",
    "4h": "4 saat",
    "1d": "Günlük"
}

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ])
    df["close"] = pd.to_numeric(df["close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def calculate_score(df):
    score = 0
    close = df["close"]
    
    rsi = RSIIndicator(close).rsi()
    macd_line = MACD(close).macd()
    macd_signal = MACD(close).macd_signal()
    ema = EMAIndicator(close, window=20).ema_indicator()

    latest_rsi = rsi.iloc[-1]
    latest_macd = macd_line.iloc[-1]
    latest_macd_signal = macd_signal.iloc[-1]
    latest_price = close.iloc[-1]
    latest_ema = ema.iloc[-1]

    # RSI
    if latest_rsi > 70:
        score += 1
    elif latest_rsi > 55:
        score += 2
    elif latest_rsi > 45:
        score += 1.5
    elif latest_rsi < 30:
        score += 0
    else:
        score += 1

    # MACD
    if latest_macd > latest_macd_signal:
        score += 2.5
    else:
        score += 1

    # EMA
    if latest_price > latest_ema:
        score += 2
    else:
        score += 1

    # Golden/Death Cross
    ema50 = EMAIndicator(close, window=50).ema_indicator()
    ema200 = EMAIndicator(close, window=200).ema_indicator()
    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 2  # Golden cross
    else:
        score += 0.5  # Death cross

    return round(score, 2)

def analyze_coin(symbol):
    scores = {}
    messages = []
    for tf in TIMEFRAMES:
        df = get_klines(symbol, tf)
        score = calculate_score(df)
        scores[tf] = score

        if score >= 7:
            label = "Güçlü Boğa"
        elif score >= 5:
            label = "Boğa"
        elif score >= 3.5:
            label = "Nötr"
        else:
            label = "Ayı"

        messages.append(f"⏱ {TIMEFRAMES[tf]}: {score}/10 → {label}")

    avg_score = round(np.mean(list(scores.values())), 2)
    if avg_score >= 7:
        final = "📈 Güçlü Boğa"
    elif avg_score >= 5:
        final = "📈 Boğa"
    elif avg_score >= 3.5:
        final = "📊 Nötr"
    else:
        final = "📉 Ayı"

    price = get_klines(symbol, "1h")["close"].iloc[-1]

    message = f"📊 {symbol} Teknik Analiz Özeti\n\n" + "\n".join(messages)
    message += f"\n\n🔎 Ortalama: {avg_score}/10\n💬 Genel Yorum: {final}"
    message += f"\n💵 Güncel Fiyat: {round(price, 2)} USDT"

    return message

def is_valid_symbol(symbol):
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    data = response.json()
    valid_symbols = [s["symbol"] for s in data["symbols"] if s["symbol"].endswith("USDT")]
    return symbol in valid_symbols

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    text = message.text.strip().upper()
    if is_valid_symbol(text):
        try:
            result = analyze_coin(text)
            bot.send_message(message.chat.id, result)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Teknik analiz sırasında hata oluştu:\n{str(e)}")
    else:
        bot.send_message(message.chat.id, "❌ Coin desteklenmiyor veya yanlış yazıldı.")

bot.polling()
