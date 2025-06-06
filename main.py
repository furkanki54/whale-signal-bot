import requests
import numpy as np
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = TeleBot(TELEGRAM_TOKEN)

def get_klines(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    return r.json()

def rsi(data, period=14):
    close = np.array([float(x[4]) for x in data])
    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.convolve(gain, np.ones(period), 'valid') / period
    avg_loss = np.convolve(loss, np.ones(period), 'valid') / period
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1]

def macd(data):
    close = np.array([float(x[4]) for x in data])
    ema12 = close[-12:].mean()
    ema26 = close[-26:].mean()
    return ema12 - ema26

def ema(data, period=50):
    close = np.array([float(x[4]) for x in data])
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(close, weights, mode='full')[:len(close)]
    return a[-1]

def analyze(symbol):
    intervals = ["15m", "1h", "4h", "1d"]
    scores = []
    messages = []

    for interval in intervals:
        data = get_klines(symbol, interval, 100)
        if not data or len(data) < 60:
            messages.append(f"❌ {interval} verisi eksik.")
            continue

        rsi_val = rsi(data)
        macd_val = macd(data)
        ema_val = ema(data)

        score = 0
        comment = []

        if rsi_val > 70:
            comment.append("RSI yüksek (aşırı alım)")
        elif rsi_val < 30:
            comment.append("RSI düşük (aşırı satım)")
            score += 2
        else:
            comment.append("RSI nötr")

        if macd_val > 0:
            comment.append("MACD al sinyali")
            score += 1
        else:
            comment.append("MACD sat sinyali")

        if float(data[-1][4]) > ema_val:
            comment.append("Fiyat EMA üstünde (boğa)")
            score += 1
        else:
            comment.append("Fiyat EMA altında (ayı)")

        messages.append(f"⏱ {interval} → Puan: {score}/4\n• " + "\n• ".join(comment))
        scores.append(score)

    avg_score = round(np.mean(scores), 2)
    mood = "📈 Boğa" if avg_score >= 2 else "📉 Ayı"

    price = float(data[-1][4])
    result = f"""📊 {symbol} Teknik Analizi:
Fiyat: ${price}
{chr(10).join(messages)}

🔎 Ortalama Skor: {avg_score}/4 → {mood}
"""
    return result

@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    symbol = msg.text.strip().upper()
    try:
        result = analyze(symbol)
        bot.send_message(msg.chat.id, result)
    except Exception as e:
        bot.send_message(msg.chat.id, f"⚠️ Hata: {e}")

bot.polling()
