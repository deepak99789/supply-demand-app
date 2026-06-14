import os, pandas as pd, yfinance as yf, requests, time

# ----------------- CONFIGURATION -----------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"
CHANNEL_IDS = {
    "Indian Stocks": "-1004441153450", "US Stocks": "-1004457256685", 
    "Forex": "-1004448848917", "Commodities": "-1004448848917", "Crypto": "-1004451326458"
}
DB_FILE = "zones_db.csv"

# ----------------- ASSETS & TIMEFRAMES -----------------
ASSETS_MASTER = {
    "Forex": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X",
            "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
            "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
            "CADJPY=X", "CADCHF=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "CHFJPY=X",
            "USDSGD=X", "USDHKD=X", "USDMXN=X", "USDSEK=X", "USDTRY=X", "EURTRY=X", "GBPSEK=X"
        ], # Baaki pairs yahan add karein
    "Commodities": [
            "GC=F", "SI=F", "PL=F", "PA=F", "CL=F", "BZ=F", "NG=F", "HG=F", "RB=F", "HO=F", "ZC=F", "ZS=F", "ZW=F"
        ],
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS"], # Nifty 100 yahan complete karein
    "US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

TIMEFRAMES_MASTER = {
    "5 Min": "5m", "15 Min": "15m", "30 Min": "30m", "45 Min": "45m", 
    "75 Min": "75m", "125 Min": "125m", "1 Hour": "1h", "2 Hour": "2h", 
    "4 Hour": "4h", "5 Hour": "5h", "6 Hour": "6h", "8 Hour": "8h", 
    "10 Hour": "10h", "12 Hour": "12h", "16 Hour": "16h", "Daily": "1d", "Weekly": "1wk"
}

def send_alert(category, message):
    try:
        target_id = CHANNEL_IDS.get(category, CHANNEL_IDS["Forex"])
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": target_id, "text": message, "parse_mode": "Markdown"})
    except: pass

def start_automatic_pipeline():
    if not os.path.exists(DB_FILE): return
    db_df = pd.read_csv(DB_FILE)

    for idx, row in db_df.iterrows():
        try:
            live_price = yf.Ticker(row['Symbol']).history(period="1d").iloc[-1]['Close']
            gap = abs(row['Proximal'] - row['Distal'])

            # 1. ZONE ENTRY ALERT
            if row["Triggered"] == "WAITING":
                if (row['Type'] == "Demand" and live_price <= row['Proximal']) or \
                   (row['Type'] == "Supply" and live_price >= row['Proximal']):
                    send_alert(row['Category'], f"📥 *ZONE ENTRY ALERT*\nAsset: {row['Symbol']}\nPrice entered the zone!")
                    db_df.at[idx, "Triggered"] = "ENTRY_DONE"
            
            # 2. PRE-ENTRY WARNING
            elif row["Triggered"] == "NO":
                if (row['Type'] == "Demand" and live_price <= (row['Proximal'] + gap)) or \
                   (row['Type'] == "Supply" and live_price >= (row['Proximal'] - gap)):
                    send_alert(row['Category'], f"⚠️ *PRE-ENTRY WARNING*\nAsset: {row['Symbol']}\nPrice approaching zone!")
                    db_df.at[idx, "Triggered"] = "WAITING"
        except: continue
    
    db_df.to_csv(DB_FILE, index=False)

def trigger_fresh_alert(new_zone, category):
    msg = (
        f"🟢 *NEW FRESH ZONE*\n\n"
        f"▪️ *SYMBOL :* `{new_zone['Symbol']}`\n"
        f"▪️ *TIMEFRAME :* `{new_zone['Timeframe']}`\n"
        f"▪️ *PATTERN :* `{new_zone['Pattern']}`\n"
        f"▪️ *TYPE :* `{new_zone['Type'].upper()}`\n"
        f"▪️ *BASE COUNT :* `{new_zone['Base_Count']}`\n"
        f"▪️ *LEGOUT COUNT :* `{new_zone['Legout_Count']}`\n"
        f"▪️ *STATUS :* `FRESH`\n"
        f"▪️ *PROXIMAL LINE :* `{new_zone['Proximal']}`\n"
        f"▪️ *DISTAL LINE :* `{new_zone['Distal']}`\n"
        f"▪️ *DATE OF ZONE FORMED :* `{new_zone['Formed_At']}`"
    )
    send_alert(category, msg)

if __name__ == "__main__":
    while True:
        start_automatic_pipeline()
        time.sleep(300)
