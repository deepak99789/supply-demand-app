import yfinance as yf
import pandas as pd
import requests
import json
import os

# -------------------------------------------------------------------
# ⚙️ TELEGRAM CONFIGURATION (Apna Token aur Chat ID Yahan Dalein)
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"  # <-- Token daalna na bhulein
TELEGRAM_CHAT_ID = "513065799"  # <-- Chat ID daalna na bhulein

def send_telegram_alert(message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN" or TELEGRAM_CHAT_ID == "YAHAN_APNI_CHAT_ID_PASTE_KAREIN":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# -------------------------------------------------------------------
# MASTER DATABASE (Filtered Nifty, Nasdaq, All Forex, All Commodities)
# -------------------------------------------------------------------
def get_complete_asset_database():
    return {
        "Indian Stocks (Filtered Alpha Nifty)": [
            "ADANIENT.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "AXISBANK.NS", 
            "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BANKBARODA.NS", "BHEL.NS", "BPCL.NS", 
            "BHARTIARTL.NS", "COALINDIA.NS", "DLF.NS", "GAIL.NS", "GMRINFRA.NS", 
            "HAL.NS", "HCLTECH.NS", "HDFCBANK.NS", "HINDALCO.NS", "ICICIBANK.NS", 
            "ITC.NS", "IRCTC.NS", "IRFC.NS", "INDUSTOWER.NS", "INDUSINDBK.NS", 
            "INFY.NS", "INTERGLOBE.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JSWSTEEL.NS", 
            "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", 
            "ONGC.NS", "PFC.NS", "POWERGRID.NS", "PNB.NS", "RELIANCE.NS", 
            "SBIN.NS", "SUNPHARMA.NS", "SUZLON.NS", "TATAMOTORS.NS", "TATAPOWER.NS", 
            "TATASTEEL.NS", "TCS.NS", "TITAN.NS", "TRENT.NS", "VEDL.NS", "WIPRO.NS", "ZOMATO.NS"
        ],
        "US Stocks (Top Nasdaq Alpha)": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "NFLX", "AMD"
        ],
        "Forex (All Majors, Minors & Crosses)": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURCAD=X", "EURCHF=X", "GBPCAD=X",
            "CHFJPY=X", "NZDJPY=X", "CADJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X", "EURAUD=X",
            "EURNZD=X", "GBPAUD=X", "GBPNZD=X", "GBPCHF=X", "CADCHF=X", "NZDCHF=X"
        ],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "Commodities (Full Suite)": [
            "GC=F", "SI=F", "HG=F", "ZN=F", "CL=F", "BZ=F", "NG=F", "PL=F", "PA=F"
        ]
    }

def resample_data(df, timeframe_str):
    if df.empty: return df
    df = df.copy()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    if timeframe_str in ['5m', '15m', '30m', '1h', '1d', '1wk']:
        return df
    resample_map = {
        "45m": "45min", "75m": "75min", "125m": "125min", 
        "2h": "2h", "4h": "4h", "5h": "5h", "6h": "6h", "8h": "8h", "10h": "10h", "16h": "16h"
    }
    rule = resample_map.get(timeframe_str)
    if not rule: return df
    return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

def scan_supply_demand_zones(df, symbol_name, tf_name):
    zones = []
    if len(df) < 12: return zones
    df = df.copy()
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(5, len(df) - 3):
        for num_base in [1, 2, 3]:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base
            
            if legout_idx >= len(df): continue
            
            legin = df.iloc[legin_idx]
            legout = df.iloc[legout_idx]
            bases = df.iloc[base_indices]
            
            # Legout and Legin Body Filter
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: continue
            
            # Base Candles Validation
            valid_bases = True
            for _, base in bases.iterrows():
                if base['body_size'] > (legin['body_size'] * 0.5):
                    valid_bases = False
                    break
            if not valid_bases: continue
            if legout['body_size'] <= legin['body_size']: continue
            
            # Calculate Dynamic Legout Count (Consecutive candles in same direction)
            legout_count = 1
            direction_green = legout['is_green']
            for k in range(legout_idx + 1, len(df)):
                if df.iloc[k]['is_green'] == direction_green and df.iloc[k]['body_ratio'] >= 50:
                    legout_count += 1
                else:
                    break
                    
            follow_up_idx = legout_idx + legout_count
            if follow_up_idx > len(df): continue
            
            legin_green, legout_green = legin['is_green'], legout['is_green']
            pattern, z_type, proximal, distal = None, None, 0.0, 0.0
            
            if legin_green and legout_green:
                pattern, z_type = "RBR", "Demand"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif legin_green and not legout_green:
                pattern, z_type = "RBD", "Supply"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
            elif not legin_green and legout_green:
                pattern, z_type = "DBR", "Demand"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif not legin_green and not legout_green:
                pattern, z_type = "DBD", "Supply"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
                
            # Check Status (Fresh or Violated)
            status = "FRESH"
            for j in range(legout_idx + 1, len(df)):
                if "Demand" in z_type and df.iloc[j]['Low'] < distal:
                    status = "VIOLATED"
                    break
                if "Supply" in z_type and df.iloc[j]['High'] > distal:
                    status = "VIOLATED"
                    break
                    
            if status == "FRESH":
                zones.append({
                    "Symbol": symbol_name,
                    "Timeframe": tf_name,
                    "Pattern": pattern,
                    "Type": z_type,
                    "Base Count": num_base,
                    "Legout Count": legout_count,
                    "Status": status,
                    "Proximal": round(proximal, 4),
                    "Distal": round(distal, 4),
                    "Formed At": df.index[i].strftime('%Y-%m-%d %H:%M')
                })
    return zones

# -------------------------------------------------------------------
# AUTOMATED PIPELINE EXECUTION
# -------------------------------------------------------------------
if __name__ == "__main__":
    assets_master = get_complete_asset_database()
    
    target_timeframes = {
        "5 Min": "5m", "15 Min": "15m", "30 Min": "30m", "45 Min": "45m", "75 Min": "75m", "125 Min": "125m",
        "1 Hour": "1h", "2 Hour": "2h", "4 Hour": "4h", "5 Hour": "5h", "6 Hour": "6h", "8 Hour": "8h",
        "10 Hour": "10h", "16 Hour": "16h", "Daily": "1d", "Weekly": "1wk"
    }
    
    print("Starting structural global sweep with premium alert formatting...")
    for category, symbols in assets_master.items():
        for symbol in symbols:
            for tf_label, tf_code in target_timeframes.items():
                
                if tf_code in ["5m", "15m", "30m", "45m", "75m", "125m"]:
                    fetch_interval, history_period = "5m", "59d"
                elif tf_code in ["1h", "2h", "4h", "5h", "6h", "8h", "10h", "16h"]:
                    fetch_interval, history_period = "1h", "360d"
                else:
                    fetch_interval, history_period = "1d", "5y"
                
                try:
                    raw_feed = yf.Ticker(symbol).history(period=history_period, interval=fetch_interval)
                    if raw_feed.empty: continue
                    
                    processed_feed = resample_data(raw_feed, tf_code)
                    fresh_zones = scan_supply_demand_zones(processed_feed, symbol, tf_label)
                    
                    for zone in fresh_zones:
                        emoji = "🟢" if zone['Type'] == "Demand" else "🔴"
                        alert_msg = (
                            f"{emoji} *NEW ZONE DETECTED* {emoji}\n\n"
                            f"▪️ *SYMBOL :* `{zone['Symbol']}`\n"
                            f"▪️ *TIMEFRAME :* `{zone['Timeframe']}`\n"
                            f"▪️ *PATTERN :* `{zone['Pattern']}`\n"
                            f"▪️ *TYPE :* `{zone['Type'].upper()}`\n"
                            f"▪️ *BASE COUNT :* `{zone['Base Count']}`\n"
                            f"▪️ *LEGOUT COUNT :* `{zone['Legout Count']}`\n"
                            f"▪️ *STATUS :* `{zone['Status']}`\n"
                            f"▪️ *PROXIMAL LINE :* `{zone['Proximal']}`\n"
                            f"▪️ *DISTAL LINE :* `{zone['Distal']}`\n"
                            f"▪️ *DATE OF ZONE FORMED :* `{zone['Formed At']}`\n\n"
                            
                        )
                        send_telegram_alert(alert_msg)
                except Exception as e:
                    continue
    print("Sweep finished successfully.")
