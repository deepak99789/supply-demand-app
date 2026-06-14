import os
import pandas as pd
import yfinance as yf
import requests

# -------------------------------------------------------------------
# ⚙️ MULTI-CHANNEL TELEGRAM CONFIGURATION
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN"

# Apne charo channels ki alag-alag Chat ID yahan dalein:
CHANNEL_IDS = {
    "Indian Stocks": "YAHAN_NIFTY_CHANNEL_CHAT_ID_DALEIN",
    "US Stocks": "YAHAN_US_STOCKS_CHANNEL_CHAT_ID_DALEIN",
    "Forex_Commodity": "YAHAN_FOREX_COMMODITY_CHANNEL_CHAT_ID_DALEIN",
    "Crypto": "YAHAN_CRYPTO_CHANNEL_CHAT_ID_DALEIN"
}

DB_FILE = "zones_db.csv"

# Dynamic Message Router
def send_market_specific_alert(category, message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN": return
    
    # Target channel select karne ka logic
    if "Indian" in category: target_id = CHANNEL_IDS["Indian Stocks"]
    elif "US" in category: target_id = CHANNEL_IDS["US Stocks"]
    elif "Crypto" in category: target_id = CHANNEL_IDS["Crypto"]
    else: target_id = CHANNEL_IDS["Forex_Commodity"] # Forex aur Commodities dono isme jayenge

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": target_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception:
        pass

# -------------------------------------------------------------------
# ASSETS MASTER DATABASE (Categorized for proper routing)
# -------------------------------------------------------------------
ASSETS_MASTER = {
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"],
    "US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"],
    "Commodities": ["GC=F", "CL=F", "NG=F"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}
TIMEFRAMES = {"1 Hour": "1h", "4 Hour": "4h", "Daily": "1d"}

def resample_data(df, timeframe_str):
    if df.empty or timeframe_str in ['1h', '1d']: return df
    df = df.copy()
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    rule = "4h" if timeframe_str == "4h" else timeframe_str
    return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

def find_latest_zone(df, symbol_name, tf_name, category):
    if len(df) < 12: return None
    df = df.copy()
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(len(df) - 4, 5, -1):
        for num_base in [1, 2, 3]:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base
            
            if legout_idx >= len(df): continue
            
            legin = df.iloc[legin_idx]
            legout = df.iloc[legout_idx]
            bases = df.iloc[base_indices]
            
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: continue
            if legout['body_size'] <= legin['body_size']: continue
            
            legin_green, legout_green = legin['is_green'], legout['is_green']
            pattern, z_type, proximal, distal = None, None, 0.0, 0.0
            
            if legin_green and legout_green: pattern, z_type = "RBR", "Demand"
            elif legin_green and not legout_green: pattern, z_type = "RBD", "Supply"
            elif not legin_green and legout_green: pattern, z_type = "DBR", "Demand"
            elif not legin_green and not legout_green: pattern, z_type = "DBD", "Supply"
            
            if z_type == "Demand":
                proximal, distal = bases['High'].max(), bases['Low'].min()
                target_price = proximal + (abs(proximal - distal) * 2)
            else:
                proximal, distal = bases['Low'].min(), bases['High'].max()
                target_price = proximal - (abs(proximal - distal) * 2)
                
            return {
                "Symbol": symbol_name, "Timeframe": tf_name, "Pattern": pattern, "Type": z_type,
                "Proximal": round(proximal, 4), "Distal": round(distal, 4), "Target": round(target_price, 4),
                "Status": "FRESH", "Formed_At": df.index[i].strftime('%Y-%m-%d %H:%M'), "Triggered": "NO", "Category": category
            }
    return None

def start_automatic_pipeline():
    print("🚀 Starting Segmented Multi-Channel Institutional Pipeline...")
    
    if os.path.exists(DB_FILE):
        db_df = pd.read_csv(DB_FILE)
        if "Category" not Red in db_df.columns: db_df["Category"] = "Forex"
    else:
        db_df = pd.DataFrame(columns=["Symbol", "Timeframe", "Pattern", "Type", "Proximal", "Distal", "Target", "Status", "Formed_At", "Triggered", "Category"])

    # PHASE 1: TRACK ACTIVE POSITION EVENTS & ROUTE TO CORRECT CHANNEL
    if not db_df.empty:
        for idx, row in db_df.iterrows():
            if row["Status"] in ["SL HIT", "TARGET"]: continue
            
            symbol = row["Symbol"]
            cat = row["Category"]
            tf_code = "1h" if row["Timeframe"] == "1 Hour" else ("4h" if row["Timeframe"] == "4 Hour" else "1d")
            
            try:
                live_feed = yf.Ticker(symbol).history(period="5d", interval="1h")
                if live_feed.empty: continue
                live_data = resample_data(live_feed, tf_code)
                
                last_candle = live_data.iloc[-1]
                last_low, last_high = last_candle["Low"], last_candle["High"]
                
                if row["Type"] == "Demand":
                    if row["Triggered"] == "NO" and last_low <= row["Proximal"]:
                        db_df.at[idx, "Triggered"] = "YES"
                        send_market_specific_alert(cat, f"📥 *ZONE ENTRY TAKEN* 📥\n\n▪️ *Asset:* `{symbol}`\n▪️ *Type:* `DEMAND`\n▪️ *Price:* `{last_low}`\n🎯 *Target (1:2):* `{row['Target']}`")
                    
                    if db_df.at[idx, "Triggered"] == "YES":
                        if last_low < row["Distal"]:
                            db_df.at[idx, "Status"] = "SL HIT"
                            send_market_specific_alert(cat, f"🔴 *STOP LOSS HIT (SL)* 🔴\n\n▪️ *Asset:* `{symbol}`\n❌ *Status:* `SL Triggered below {row['Distal']}`")
                        elif last_high >= row["Target"]:
                            db_df.at[idx, "Status"] = "TARGET"
                            send_market_specific_alert(cat, f"💰 *TARGET HIT (1:2 RR)* 🎉\n\n▪️ *Asset:* `{symbol}`\n🔥 *Status:* `Profit Secured at {row['Target']}`")
                
                else: # Supply Zone
                    if row["Triggered"] == "NO" and last_high >= row["Proximal"]:
                        db_df.at[idx, "Triggered"] = "YES"
                        send_market_specific_alert(cat, f"📥 *ZONE ENTRY TAKEN (SHORT)* 📥\n\n▪️ *Asset:* `{symbol}`\n▪️ *Type:* `SUPPLY`\n▪️ *Price:* `{last_high}`\n🎯 *Target (1:2):* `{row['Target']}`")
                    
                    if db_df.at[idx, "Triggered"] == "YES":
                        if last_high > row["Distal"]:
                            db_df.at[idx, "Status"] = "SL HIT"
                            send_market_specific_alert(cat, f"🔴 *STOP LOSS HIT (SL)* 🔴\n\n▪️ *Asset:* `{symbol}`\n❌ *Status:* `SL Triggered above {row['Distal']}`")
                        elif last_low <= row["Target"]:
                            db_df.at[idx, "Status"] = "TARGET"
                            send_market_specific_alert(cat, f"💰 *TARGET HIT (1:2 RR)* 🎉\n\n▪️ *Asset:* `{symbol}`\n🔥 *Status:* `Profit Secured at {row['Target']}`")
            except Exception:
                continue

    # PHASE 2: SCAN FOR NEW FRESH ZONES & SEGREGATE
    for category, symbols in ASSETS_MASTER.items():
        for symbol in symbols:
            for tf_label, tf_code in TIMEFRAMES.items():
                try:
                    period = "360d" if tf_code == "1h" else "5y"
                    raw_feed = yf.Ticker(symbol).history(period=period, interval="1h" if tf_code != "1d" else "1d")
                    if raw_feed.empty: continue
                    
                    processed_feed = resample_data(raw_feed, tf_code)
                    new_zone = find_latest_zone(processed_feed, symbol, tf_label, category)
                    
                    if new_zone:
                        duplicate = db_df[(db_df["Symbol"] == symbol) & (db_df["Formed_At"] == new_zone["Formed_At"]) & (db_df["Timeframe"] == tf_label)]
                        if duplicate.empty:
                            db_df = pd.concat([db_df, pd.DataFrame([new_zone])], ignore_index=True)
                            
                            emoji = "🟢" if new_zone['Type'] == "Demand" else "🔴"
                            alert_msg = (
                                f"{emoji} *AUTOMATIC NEW ZONE* {emoji}\n\n"
                                f"▪️ *SYMBOL :* `{new_zone['Symbol']}`\n"
                                f"▪️ *TIMEFRAME :* `{new_zone['Timeframe']}`\n"
                                f"▪️ *TYPE :* `{new_zone['Type'].upper()}`\n"
                                f"▪️ *PROXIMAL :* `{new_zone['Proximal']}`\n"
                                f"▪️ *DISTAL (SL) :* `{new_zone['Distal']}`\n"
                                f"▪️ *TARGET (1:2) :* `{new_zone['Target']}`\n"
                            )
                            send_market_specific_alert(category, alert_msg)
                except Exception:
                    continue

    db_df.to_csv(DB_FILE, index=False)
    print("💾 Segmented Database Saved Successfully.")

if __name__ == "__main__":
    start_automatic_pipeline()
