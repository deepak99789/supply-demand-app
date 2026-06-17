import os
import pandas as pd
import yfinance as yf
import requests
import time

# -------------------------------------------------------------------
# ⚙️ CONFIGURATION
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"
CHANNEL_IDS = {"Indian Stocks": "-1004441153450", "US Stocks": "-1004457256685", "Forex": "YOUR_ID", "Commodities": "-1004448848917", "Crypto": "-1004451326458"}
DB_FILE = "zones_db.csv"

ASSETS_MASTER = {
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X",
            "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
            "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
            "CADJPY=X", "CADCHF=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "CHFJPY=X", ],
    "Indian Stocks": ["RELIANCE.NS"],
    "US Stocks": ["AAPL"],
    "Crypto": ["BTC-USD"]
}

TIMEFRAMES_MASTER = {
    "5 Min": {"base_interval": "5m", "period": "5d"},
    "15 Min": {"base_interval": "15m", "period": "5d"},
    "30 Min": {"base_interval": "30m", "period": "5d"},
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

def send_msg(cat, msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_IDS.get(cat, CHANNEL_IDS["Forex"]), "text": msg, "parse_mode": "Markdown"})
    except: pass

def get_proximal_distal(base, ztype):
    is_green = base['Close'] > base['Open']
    if ztype == "Demand": return (base['Close'] if is_green else base['Open'], base['Low'])
    return (base['Open'] if is_green else base['Close'], base['High'])

def apply_resampling(df, tf):
    if df.empty: return df
    df = df.copy()
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    rule = TIMEFRAMES_MASTER[tf].get("resample_rule")
    return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna() if rule else df

def find_latest_zone(df, sym, tf, cat):
    if len(df) < 15: return None
    df = df.copy()
    df['body_ratio'] = (df['Close'] - df['Open']).abs() / (df['High'] - df['Low']).replace(0, 0.0001) * 100
    for i in range(len(df) - 6, 5, -1):
        for num_base in [1, 2, 3]:
            legin, legout = df.iloc[i-1], df.iloc[i+num_base]
            if legin['body_ratio'] < 70 or legout['body_ratio'] < 70: continue
            z_type = "Demand" if (legin['Close'] < legin['Open'] and legout['Close'] > legout['Open']) or (legin['Close'] > legin['Open'] and legout['Close'] > legout['Open']) else "Supply"
            bases = df.iloc[i : i+num_base]
            prox_list = [get_proximal_distal(bases.iloc[k], z_type)[0] for k in range(len(bases))]
            dist_list = [get_proximal_distal(bases.iloc[k], z_type)[1] for k in range(len(bases))]
            prox, dist = (max(prox_list), min(dist_list)) if z_type == "Demand" else (min(prox_list), max(prox_list))
            return {"Symbol": sym, "Timeframe": tf, "Pattern": f"{'R' if legin['Close']>legin['Open'] else 'D'}B{'R' if legout['Close']>legout['Open'] else 'D'}", "Type": z_type, "Proximal": round(prox, 4), "Distal": round(dist, 4), "Target": round(prox + (abs(prox-dist)*2) if z_type=="Demand" else prox - (abs(prox-dist)*2), 4), "Status": "FRESH", "Formed At": df.index[i].strftime('%Y-%m-%d %H:%M'), "Base Count": num_base, "Approached": "NO", "Triggered": "NO", "Category": cat}
    return None

def start_pipeline():
    db_df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["Symbol", "Timeframe", "Pattern", "Type", "Proximal", "Distal", "Target", "Status", "Formed At", "Base Count", "Approached", "Triggered", "Category"])
    # PHASE 1: TRACKING
    for idx, row in db_df.iterrows():
        if row["Status"] in ["SL HIT", "TARGET"]: continue
        price = yf.Ticker(row["Symbol"]).history(period="1d", interval="15m")["Close"].iloc[-1]
        if row["Approached"] == "NO" and abs(price - row["Proximal"]) <= abs(row["Proximal"] - row["Distal"]):
            db_df.at[idx, "Approached"] = "YES"
            send_msg(row["Category"], f"⚠️ *APPROACHING:* `{row['Symbol']}` is near zone!")
        if row["Triggered"] == "NO" and ((row["Type"]=="Demand" and price <= row["Proximal"]) or (row["Type"]=="Supply" and price >= row["Proximal"])):
            db_df.at[idx, "Triggered"] = "YES"
            send_msg(row["Category"], f"📥 *ENTRY TRIGGERED:* `{row['Symbol']}` at `{price}`")
        if row["Triggered"] == "YES":
            if (row["Type"]=="Demand" and (price <= row["Distal"] or price >= row["Target"])) or (row["Type"]=="Supply" and (price >= row["Distal"] or price <= row["Target"])):
                db_df.at[idx, "Status"] = "SL HIT" if (row["Type"]=="Demand" and price <= row["Distal"]) or (row["Type"]=="Supply" and price >= row["Distal"]) else "TARGET"
                send_msg(row["Category"], f"🏁 *ZONE CLOSED:* `{row['Symbol']}` - {db_df.at[idx, 'Status']}")
    # PHASE 2: SCAN
    for cat, syms in ASSETS_MASTER.items():
        for sym in syms:
            time.sleep(0.5)
            for tf, conf in TIMEFRAMES_MASTER.items():
                data = apply_resampling(yf.Ticker(sym).history(period=conf["period"], interval=conf["base_interval"]), tf)
                zone = find_latest_zone(data, sym, tf, cat)
                if zone and db_df[(db_df["Symbol"]==sym) & (db_df["Formed At"]==zone["Formed At"]) & (db_df["Timeframe"]==tf)].empty:
                    db_df = pd.concat([db_df, pd.DataFrame([zone])], ignore_index=True)
                    send_msg(cat, f"🟢 *NEW ZONE DETECTED*\n\n▪️ *SYMBOL:* `{zone['Symbol']}`\n▪️ *TF:* `{zone['Timeframe']}`\n▪️ *PATTERN:* `{zone['Pattern']}`\n▪️ *TYPE:* `{zone['Type']}`\n▪️ *BASE COUNT:* `{zone['Base Count']}`\n▪️ *PROXIMAL:* `{zone['Proximal']}`\n▪️ *DISTAL:* `{zone['Distal']}`\n▪️ *TARGET:* `{zone['Target']}`\n▪️ *DATE:* `{zone['Formed At']}`")
    db_df.to_csv(DB_FILE, index=False)

if __name__ == "__main__":
    start_pipeline()
