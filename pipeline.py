import yfinance as yf
import pandas as pd
import requests
import json
import os

# -------------------------------------------------------------------
# ⚙️ TELEGRAM CONFIGURATION (Apna Token aur Chat ID Yahan Dalein)
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"  # <-- Apne bot ka token yahan dalein
TELEGRAM_CHAT_ID = "513065799"  # <-- Apni chat id yahan dalein

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
# MASTER DATABASE (Nifty 100, Forex, Crypto)
# -------------------------------------------------------------------
def get_complete_asset_database():
    return {
        "Indian Stocks (Nifty 100)": [
            "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS",
            "ASIANPAINT.NS", "ASTRAL.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS",
            "BERGEPAINT.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BOSCHLTD.NS", "BRITANNIA.NS", "CANBK.NS", "CGPOWER.NS",
            "CHOLAMAND.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "CUMMINSIND.NS", "DLF.NS", "DABUR.NS", "DIVISLAB.NS",
            "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS", "GMRINFRA.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HAL.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "ITC.NS",
            "INDIANB.NS", "INDHOTEL.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS", "INFY.NS", "INTERGLOBE.NS",
            "JINDALSTEL.NS", "JIOFIN.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KPITTECH.NS", "KOTAKBANK.NS", "LT.NS", "LTIM.NS", "LICHSGFIN.NS",
            "LUPIN.NS", "M&M.NS", "MARICO.NS", "MARUTI.NS", "MAXHEALTH.NS", "NTPC.NS", "NESTLEIND.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS",
            "PIIND.NS", "PFC.NS", "POWERGRID.NS", "PNB.NS", "RELIANCE.NS", "SBICARD.NS", "SBILIFE.NS", "SRF.NS", "MOTHERSON.NS", "SHREECEM.NS",
            "SHRIRAMFIN.NS", "SIEMENS.NS", "SONACOMS.NS", "SBIN.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUZLON.NS", "TATACOMM.NS", "TATACONSUM.NS",
            "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TRENT.NS",
            "UPL.NS", "ULTRACEMCO.NS", "VBL.NS", "VEDL.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZOMATO.NS"
        ],
        "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "EURGBP=X", "GBPJPY=X"],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
    }

def resample_data(df, timeframe_str):
    if df.empty: return df
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    if timeframe_str in ['1h', '1d']: return df
    resample_map = {"2h": "2h", "4h": "4h"}
    rule = resample_map.get(timeframe_str)
    if not rule: return df
    return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

def scan_supply_demand_zones(df, symbol_name, tf_name):
    zones = []
    if len(df) < 10: return zones
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(5, len(df) - 2):
        for num_base in [1, 2, 3]:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base
            follow_up_idx = legout_idx + 1
            
            if follow_up_idx >= len(df): continue
            legin, legout, follow_up, bases = df.iloc[legin_idx], df.iloc[legout_idx], df.iloc[follow_up_idx], df.iloc[base_indices]
            
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: continue
            valid_bases = True
            for _, base in bases.iterrows():
                if base['body_size'] > (legin['body_size'] * 0.5):
                    valid_bases = False
                    break
            if not valid_bases: continue
            if legout['body_size'] <= legin['body_size']: continue
            if legout['is_green'] != follow_up['is_green']: continue
                
            legin_green, legout_green = legin['is_green'], legout['is_green']
            zone_type, proximal, distal = None, 0.0, 0.0
            
            if legin_green and legout_green:
                zone_type = "RBR (Demand)"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif legin_green and not legout_green:
                zone_type = "RBD (Supply)"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
            elif not legin_green and legout_green:
                zone_type = "DBR (Demand)"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif not legin_green and not legout_green:
                zone_type = "DBD (Supply)"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
                
            tested = False
            for j in range(follow_up_idx + 1, len(df)):
                if "Demand" in zone_type and df.iloc[j]['Low'] <= proximal:
                    tested = True
                    break
                if "Supply" in zone_type and df.iloc[j]['High'] >= proximal:
                    tested = True
                    break
                    
            if not tested:
                zones.append({
                    "Symbol": symbol_name, "Timeframe": tf_name, "Pattern Time": df.index[i].strftime('%Y-%m-%d %H:%M'),
                    "Zone Type": zone_type, "Proximal": round(proximal, 4), "Distal": round(distal, 4)
                })
    return zones

if __name__ == "__main__":
    assets_master = get_complete_asset_database()
    target_timeframes = {"1 Hour": "1h", "2 Hour": "2h", "4 Hour": "4h", "Daily": "1d"}
    
    print("Starting background multi-asset structural sweep...")
    for category, symbols in assets_master.items():
        for symbol in symbols:
            for tf_label, tf_code in target_timeframes.items():
                fetch_interval = "1h" if tf_code in ["1h", "2h", "4h"] else "1d"
                history_period = "360d" if fetch_interval == "1h" else "5y"
                
                try:
                    raw_feed = yf.Ticker(symbol).history(period=history_period, interval=fetch_interval)
                    if raw_feed.empty: continue
                    
                    processed_feed = resample_data(raw_feed, tf_code)
                    fresh_zones = scan_supply_demand_zones(processed_feed, symbol, tf_label)
                    
                    for zone in fresh_zones:
                        emoji = "🟢 AUTOMATIC DEMAND" if "Demand" in zone['Zone Type'] else "🔴 AUTOMATIC SUPPLY"
                        alert_msg = (
                            f"🤖 *AUTO-SCANNER ALERT*\n\n"
                            f"{emoji}\n"
                            f"🔹 *Asset:* `{zone['Symbol']}`\n"
                            f"⏱️ *Timeframe:* {zone['Timeframe']}\n"
                            f"📌 *Proximal:* `{zone['Proximal']}`\n"
                            f"🎚️ *Distal:* `{zone['Distal']}`\n"
                            f"📅 *Formed At:* {zone['Pattern Time']}"
                        )
                        send_telegram_alert(alert_msg)
                except Exception as e:
                    continue
    print("Background sweep finished successfully.")
