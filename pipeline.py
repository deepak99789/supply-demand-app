import os
import pandas as pd
import yfinance as yf
import requests
import time

# -------------------------------------------------------------------
# ⚙️ MULTI-CHANNEL TELEGRAM CONFIGURATION
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"

CHANNEL_IDS = {
    "Indian Stocks": "-1004441153450",
    "US Stocks": "-1004457256685",
    "Forex": "-1004448848917",
    "Commodities": "-1004448848917",
    "Crypto": "-1004451326458"
}

DB_FILE = "zones_db.csv"

def send_market_specific_alert(category, message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN": return
    if "Indian" in category: target_id = CHANNEL_IDS["Indian Stocks"]
    elif "US Stocks" in category: target_id = CHANNEL_IDS["US Stocks"]
    elif "Forex" in category: target_id = CHANNEL_IDS["Forex"]
    elif "Commodities" in category: target_id = CHANNEL_IDS["Commodities"]
    elif "Crypto" in category: target_id = CHANNEL_IDS["Crypto"]
    else: target_id = CHANNEL_IDS["Forex"]
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": target_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception: pass

# -------------------------------------------------------------------
# 🎯 MASTER DATABASE
# -------------------------------------------------------------------
ASSETS_MASTER = {
    "Forex": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X",
            "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
            "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
            "CADJPY=X", "CADCHF=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "CHFJPY=X", 
        ],
    "Commodities": [
            "GC=F", "SI=F", "PL=F", "PA=F", "CL=F", "BZ=F", "NG=F", "HG=F", "RB=F", "HO=F", "ZC=F", "ZS=F", "ZW=F"
        ],
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "SBIN.NS"],
    "US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"],
    "Crypto": ["BTC-USD"]
}

# 🛠️ ALL REQUESTED TIMEFRAMES MASTER CONFIGURATION
TIMEFRAMES_MASTER = {
    "5 Min": {"base_interval": "5m", "period": "5d"},
    "15 Min": {"base_interval": "15m", "period": "5d"},
    "30 Min": {"base_interval": "30m", "period": "5d"},
    "45 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "45min"},
    "75 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "75min"},
    "125 Min": {"base_interval": "5m", "period": "5d", "resample_rule": "125min"},
    "1 Hour": {"base_interval": "1h", "period": "360d"},
    "2 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "2h"},
    "4 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "4h"},
    "5 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "5h"},
    "6 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "6h"},
    "8 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "8h"},
    "10 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "10h"},
    "12 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "12h"},
    "16 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "16h"},
    "Daily": {"base_interval": "1d", "period": "5y"},
    "Weekly": {"base_interval": "1wk", "period": "max"}
}

def apply_resampling(df, tf_name):
    if df.empty: return df
    df = df.copy()
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    
    config = TIMEFRAMES_MASTER[tf_name]
    if "resample_rule" in config:
        rule = config["resample_rule"]
        return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    return df

def find_latest_zone(df, symbol_name, tf_name, category):
    if len(df) < 12: return None
    df = df.copy()
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(len(df) - 4, 5, -1):
        for num_base in [1]:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base
            if legout_idx >= len(df): continue
            
            legin, legout = df.iloc[legin_idx], df.iloc[legout_idx]
            bases = df.iloc[base_indices]
            
            if legin['body_ratio'] < 70 or legout['body_ratio'] < 70: continue
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
    print("🚀 Running Custom Resampled Multi-Timeframe Alert Pipeline...")
    if os.path.exists(DB_FILE): 
        db_df = pd.read_csv(DB_FILE)
    else: 
        # Yahan 'Formed At' (space ke saath) use karein
        db_df = pd.DataFrame(columns=["Symbol", "Timeframe", "Pattern", "Type", "Proximal", "Distal", "Target", "Status", "Formed At", "Base Count", "Legout Count"])
    # ... baki ka code yahan rahega ...
    # PHASE 1: TRACK ACTIVE POSITION EVENTS
    if not db_df.empty:
        for idx, row in db_df.iterrows():
            if row["Status"] in ["SL HIT", "TARGET"]: continue
            symbol, cat, tf_label = row["Symbol"], row["Category"], row["Timeframe"]
            config = TIMEFRAMES_MASTER[tf_label]
            try:
                live_feed = yf.Ticker(symbol).history(period="3d" if "Min" in tf_label else "10d", interval=config["base_interval"])
                if live_feed.empty: continue
                live_data = apply_resampling(live_feed, tf_label)
                last_candle = live_data.iloc[-1]
                last_low, last_high = last_candle["Low"], last_candle["High"]
                
                if row["Type"] == "Demand":
                    if row["Triggered"] == "NO" and last_low <= row["Proximal"]:
                        db_df.at[idx, "Triggered"] = "YES"
                        send_market_specific_alert(cat, f"📥 *ZONE ENTRY* 📥\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n▪️ *Type:* `DEMAND`\n▪️ *Price:* `{last_low}`\n🎯 *Target:* `{row['Target']}`")
                    if db_df.at[idx, "Triggered"] == "YES":
                        if last_low < row["Distal"]:
                            db_df.at[idx, "Status"] = "SL HIT"
                            send_market_specific_alert(cat, f"🔴 *STOP LOSS HIT* 🔴\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n❌ *SL Breached Below:* `{row['Distal']}`")
                        elif last_high >= row["Target"]:
                            db_df.at[idx, "Status"] = "TARGET"
                            send_market_specific_alert(cat, f"💰 *TARGET HIT* 🎉\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n🔥 *Profit Secured At:* `{row['Target']}`")
                else: # Supply
                    if row["Triggered"] == "NO" and last_high >= row["Proximal"]:
                        db_df.at[idx, "Triggered"] = "YES"
                        send_market_specific_alert(cat, f"📥 *ZONE ENTRY (SHORT)* 📥\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n▪️ *Type:* `SUPPLY`\n▪️ *Price:* `{last_high}`\n🎯 *Target:* `{row['Target']}`")
                    if db_df.at[idx, "Triggered"] == "YES":
                        if last_high > row["Distal"]:
                            db_df.at[idx, "Status"] = "SL HIT"
                            send_market_specific_alert(cat, f"🔴 *STOP LOSS HIT* 🔴\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n❌ *SL Breached Above:* `{row['Distal']}`")
                        elif last_low <= row["Target"]:
                            db_df.at[idx, "Status"] = "TARGET"
                            send_market_specific_alert(cat, f"💰 *TARGET HIT* 🎉\n\n▪️ *Asset:* `{symbol}`\n▪️ *TF:* `{tf_label}`\n🔥 *Profit Secured At:* `{row['Target']}`")
            except Exception: continue

    # PHASE 2: SCAN FOR NEW FRESH ZONES
    # PHASE 2: SCAN FOR NEW FRESH ZONES
    for category, symbols in ASSETS_MASTER.items():
        for symbol in symbols:
            time.sleep(2)
            for tf_label, config in TIMEFRAMES_MASTER.items():
                try:
                    raw_feed = yf.Ticker(symbol).history(period=config["period"], interval=config["base_interval"])
                    if raw_feed.empty: continue
                    processed_feed = apply_resampling(raw_feed, tf_label)
                    new_zone = find_latest_zone(processed_feed, symbol, tf_label, category)
                    
                    if new_zone:
                        duplicate = db_df[(db_df["Symbol"] == symbol) & 
                  (db_df["Formed At"].astype(str) == str(new_zone["Formed At"])) & 
                  (db_df["Timeframe"] == tf_label)]
                        if duplicate.empty:
                            db_df = pd.concat([db_df, pd.DataFrame([new_zone])], ignore_index=True)
                            emoji = "🟢" if new_zone['Type'] == "Demand" else "🔴"
                            
                            alert_msg = (
                                f"{emoji} *NEW ZONE DETECTED* {emoji}\n\n"
                                f"▪️ *SYMBOL :* `{new_zone['Symbol']}`\n"
                                f"▪️ *TIMEFRAME :* `{new_zone['Timeframe']}`\n"
                                f"▪️ *PATTERN :* `{new_zone['Pattern']}`\n"
                                f"▪️ *TYPE :* `{new_zone['Type'].upper()}`\n"
                                f"▪️ *STATUS :* `{new_zone['Status']}`\n"
                                f"▪️ *PROXIMAL :* `{new_zone['Proximal']}`\n"
                                f"▪️ *DISTAL :* `{new_zone['Distal']}`\n"
                                f"▪️ *TARGET :* `{new_zone['Target']}`"
                            )
                            send_market_specific_alert(category, alert_msg)
                except Exception: continue

    db_df.to_csv(DB_FILE, index=False)
    print("💾 Database Synced.")

if __name__ == "__main__":
    start_automatic_pipeline()
