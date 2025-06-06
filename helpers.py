import requests
import pandas as pd
import ta
from config import BINANCE_API_BASE

def get_klines(symbol, interval, limit=100):
    url = f"{BINANCE_API_BASE}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df
    return None

def analyze_coin(symbol):
    intervals = {
        "15 dakika": "15m",
        "1 saat": "1h",
        "4 saat": "4h",
        "Günlük": "1d"
    }

    scores = {}
    texts = []

    for label, interval in intervals.items():
        df = get_klines(symbol, interval)
        if df is None or len(df) < 30:
            texts.append(f"⏱ {label} → Veri yetersiz.")
            scores[label] = 0
            continue

        rsi = ta.momentum.RSIIndicator(df["close"]).rsi().iloc[-1]
        macd = ta.trend.MACD(df["close"])
        macd_diff = macd.macd_diff().iloc[-1]

        ema_50 = df["close"].ewm(span=50).mean().iloc[-1]
        price = df["close"].iloc[-1]

        score = 0
        details = []

        if rsi > 70:
            details.append("• RSI aşırı alımda")
            score += 1
        elif rsi > 50:
            details.append("• RSI pozitif bölgede")
            score += 2
        elif rsi > 30:
            details.append("• RSI nötr-altı")
            score += 1
        else:
            details.append("• RSI aşırı satımda")

        if macd_diff > 0:
            details.append("• MACD al sinyali")
            score += 2
        else:
            details.append("• MACD sat sinyali")

        if price > ema_50:
            details.append("• Fiyat EMA50 üzerinde")
            score += 2
        else:
            details.append("• Fiyat EMA50 altında")

        direction = "Güçlü Boğa" if score >= 7 else "Boğa" if score >= 5 else "Nötr" if score >= 3 else "Ayı"
        scores[label] = score
        texts.append(f"⏱ {label}: {score}/10 → {direction}\n" + "\n".join(details))

    avg_score = sum(scores.values()) / len(scores)
    genel_yorum = "📈 Boğa" if avg_score >= 6 else "📉 Ayı" if avg_score <= 4 else "🔄 Nötr"
    price_info = f"\n💬 Genel Yorum: {genel_yorum}\n🪙 Güncel Fiyat: {price:.2f} USDT"

    return f"{symbol} Teknik Analiz Özeti\n\n" + "\n\n".join(texts) + f"\n\n📊 Ortalama: {avg_score:.2f}/10" + price_info
