import pandas as pd
import yfinance as yf
import json
import os

# Consolidated Asset Master Database
TICKERS = {
    "Nifty100_Major": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "ICICIBANK.NS", "BHARTIARTL.NS"],
    "Nasdaq100_Major": ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "TSLA"],
    "Forex_Major": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"],
    "Crypto_Major": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "BNB-USD"],
    "Commodities_Major": ["GC=F", "CL=F", "SI=F", "NG=F"]
}

TIMEFRAMES = ["5m", "15m", "75m", "125m", "4h", "1d"]

def resample_data(df, timeframe):
    if timeframe in ["5m", "15m", "1d"]: 
        return df
    rule_map = {"75m": "75T", "125m": "125T", "4h": "240T"}
    rule = rule_map.get(timeframe)
    if not rule: 
        return df
    return df.resample(rule).agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()

def scan_zones(df):
    zones = []
    if len(df) < 10: 
        return zones
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

    for i in range(5, len(df)-2):
        for num_base in [1, 2, 3]:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base
            follow_up_idx = legout_idx + 1
            
            if follow_up_idx >= len(df): 
                continue
                
            legin = df.iloc[legin_idx]
            legout = df.iloc[legout_idx]
            follow_up = df.iloc[follow_up_idx]
            bases = df.iloc[base_indices]
            
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: 
                continue
            
            valid_bases = True
            for _, base in bases.iterrows():
                if base['body_size'] > (legin['body_size'] * 0.5):
                    valid_bases = False
                    break
            if not valid_bases: 
                continue
                
            if legout['body_size'] <= legin['body_size']: 
                continue
            if legout['is_green'] != follow_up['is_green']: 
                continue
                
            legin_green = legin['is_green']
            legout_green = legout['is_green']
            zone_type, proximal, distal = None, 0.0, 0.0
            
            if legin_green and legout_green:
                zone_type = "RBR"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif legin_green and not legout_green:
                zone_type = "RBD"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
            elif not legin_green and legout_green:
                zone_type = "DBR"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif not legin_green and not legout_green:
                zone_type = "DBD"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
                
            tested = False
            for j in range(follow_up_idx + 1, len(df)):
                if zone_type in ["RBR", "DBR"] and df.iloc[j]['Low'] <= proximal:
                    tested = True
                    break
                if zone_type in ["RBD", "DBD"] and df.iloc[j]['High'] >= proximal:
                    tested = True
                    break
                    
            zones.append({
                "time": str(df.index[i]),
                "type": zone_type,
                "proximal": float(proximal),
                "distal": float(distal),
                "status": "Tested" if tested else "Fresh"
            })
    return zones

output_db = {}

print("🚀 Starting automated supply demand engine parsing...")
for category, tickers in TICKERS.items():
    output_db[category] = {}
    for symbol in tickers:
        output_db[category][symbol] = {}
        # Base 5m logic fetch for optimized resampling pipeline structures
        df_base = yf.Ticker(symbol).history(period="60d", interval="5m")
        if df_base.empty: 
            continue
            
        for tf in TIMEFRAMES:
            df_processed = resample_data(df_base, tf)
            detected = scan_zones(df_processed)
            output_db[category][symbol][tf] = detected

with open("market_zones.json", "w") as f:
    json.dump(output_db, f, indent=4)

print("✅ Global market calculation synced successfully into market_zones.json")
