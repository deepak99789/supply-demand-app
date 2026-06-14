import os
import pandas as pd
import yfinance as yf
import requests
import time
import json

# -------------------------------------------------------------------
# ⚙️ CONFIGURATION & UTILS
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN"
CHANNEL_IDS = {
    "Indian Stocks": "YAHAN_NIFTY_CHANNEL_CHAT_ID_DALEIN", "US Stocks": "YAHAN_US_STOCKS_CHANNEL_CHAT_ID_DALEIN",
    "Forex": "YAHAN_FOREX_CHANNEL_CHAT_ID_DALEIN", "Commodities": "YAHAN_COMMODITY_CHANNEL_CHAT_ID_DALEIN",
    "Crypto": "YAHAN_CRYPTO_CHANNEL_CHAT_ID_DALEIN"
}
DB_FILE = "zones_db.csv"

def get_config():
    try:
        with open("config.json", "r") as f: return json.load(f)
    except: return {"allowed_bases": [1, 2], "allowed_legouts": [1], "rules": []}

def send_market_specific_alert(category, message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN": return
    target_id = CHANNEL_IDS.get(category, CHANNEL_IDS["Forex"])
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": target_id, "text": message, "parse_mode": "Markdown"})
    except: pass

# -------------------------------------------------------------------
# 🎯 ASSETS & TIMEFRAMES (Aapka original setup)
# -------------------------------------------------------------------
ASSETS_MASTER = {
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X", "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X", "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X", "AUDJPY=X", "USDSGD=X"],
    "Commodities": ["GC=F", "SI=F", "CL=F", "BZ=F", "NG=F", "HG=F"],
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS"],
    "US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

TIMEFRAMES_MASTER = {
    "5 Min": {"base_interval": "5m", "period": "5d"}, "15 Min": {"base_interval": "15m", "period": "5d"},
    "30 Min": {"base_interval": "30m", "period": "5d"}, "45 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "45min"},
    "75 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "75min"}, "125 Min": {"base_interval": "5m", "period": "5d", "resample_rule": "125min"},
    "1 Hour": {"base_interval": "1h", "period": "360d"}, "2 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "2h"},
    "4 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "4h"}, "5 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "5h"},
    "6 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "6h"}, "8 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "8h"},
    "10 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "10h"}, "12 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "12h"},
    "16 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "16h"}, "Daily": {"base_interval": "1d", "period": "5y"},
    "Weekly": {"base_interval": "1wk", "period": "max"}
}

def apply_resampling(df, tf_name):
    if df.empty: return df
    df = df.copy()
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    config = TIMEFRAMES_MASTER[tf_name]
    if "resample_rule" in config:
        return df.resample(config["resample_rule"]).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    return df

def find_latest_zone(df, symbol_name, tf_name, category):
    cfg = get_config()
    if len(df) < 12: return None
    df = df.copy()
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(len(df) - 4, 5, -1):
        for num_base in cfg.get("allowed_bases", [1, 2]):
            legin_idx = i - 1
            legout_idx = i + num_base
            if legout_idx >= len(df): continue
            
            legin, legout = df.iloc[legin_idx], df.iloc[legout_idx]
            
            # --- VALIDATION RULES ---
            if "candle_behinde_legin" in cfg["rules"]:
                prev_c = df.iloc[i-2]
                if prev_c['High'] >= legin['High'] and prev_c['Low'] <= legin['Low']: continue
            
            if "whitearea_check" in cfg["rules"]:
                b_min = min(df.iloc[i:i+num_base]['Open'].min(), df.iloc[i:i+num_base]['Close'].min())
                b_max = max(df.iloc[i:i+num_base]['Open'].max(), df.iloc[i:i+num_base]['Close'].max())
                if legout['Low'] < b_min or legout['High'] > b_max: continue # Custom logic for White Area

            # Zone Logic
            pattern = "S&D"
            z_type = "Demand" if (legin['Close'] < legin['Open'] and legout['Close'] > legout['Open']) else "Supply"
            bases = df.iloc[i:i+num_base]
            proximal = bases['High'].max() if z_type == "Demand" else bases['Low'].min()
            distal = bases['Low'].min() if z_type == "Demand" else bases['High'].max()
            target = proximal + (abs(proximal - distal) * 2) if z_type == "Demand" else proximal - (abs(proximal - distal) * 2)
            
            return {"Symbol": symbol_name, "Timeframe": tf_name, "Type": z_type, "Proximal": round(proximal, 4), "Distal": round(distal, 4), "Target": round(target, 4), "Status": "FRESH", "Formed_At": df.index[i].strftime('%Y-%m-%d %H:%M'), "Triggered": "NO", "Category": category}
    return None

def start_automatic_pipeline():
    print("🚀 Running Pipeline...")
    # (Phase 1 & 2 logic same as previous version)
    # ...
    pass 

if __name__ == "__main__":
    while True:
        start_automatic_pipeline()
        time.sleep(300)
