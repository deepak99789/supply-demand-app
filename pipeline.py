import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests

# Page Setup
st.set_page_config(layout="wide", page_title="Institutional Scanner")
st.markdown("<h1 style='text-align: center; color: #2ecc71;'>⚡ Institutional Matrix Scanner</h1>", unsafe_allow_html=True)

# ----------------- CONFIGURATION -----------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"
CHANNEL_IDS = {
    "Indian Stocks": "-1004441153450", "US Stocks": "-1004457256685", 
    "Forex": "-1004448848917", "Commodities": "-1004448848917", "Crypto": "-1004451326458"
}

def send_telegram_alert(category, message):
    try:
        chat_id = CHANNEL_IDS.get(category, "-1004448848917")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except: pass

# ----------------- ASSET DATABASE -----------------
ASSETS_MASTER = {
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"],
    "Indian Stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "US Stocks": ["AAPL", "MSFT", "NVDA"],
    "Crypto": ["BTC-USD", "ETH-USD"],
    "Commodities": ["GC=F", "CL=F"]
}
timeframe_dict = {"5 Min": "5m", "15 Min": "15m", "1 Hour": "1h", "4 Hour": "4h", "Daily": "1d"}

# ----------------- SCANNING ENGINE -----------------
def scan_zones(df, symbol, tf, allowed_bases, allowed_legouts):
    zones = []
    df = df.copy()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    
    for i in range(5, len(df) - 3):
        for num_base in allowed_bases:
            legout_idx = i + num_base
            if legout_idx >= len(df): continue
            
            # Legout Filter logic
            legout_count = 1 
            # (Simplified check for this example)
            if legout_count not in allowed_legouts: continue
            
            # Pattern Detection Logic
            z_type = "Demand" if df.iloc[i-1]['is_green'] else "Supply"
            proximal = df.iloc[i:i+num_base]['High'].max() if z_type == "Demand" else df.iloc[i:i+num_base]['Low'].min()
            
            zones.append({
                "Symbol": symbol, "Timeframe": tf, "Type": z_type, 
                "Proximal": round(proximal, 4), "Base Count": num_base, 
                "Legout Count": legout_count, "Status": "FRESH"
            })
    return zones

# ----------------- UI -----------------
market_cat = st.selectbox("Market Category", list(ASSETS_MASTER.keys()))
selected_symbol = st.selectbox("Symbol", ASSETS_MASTER[market_cat])
selected_tf = st.multiselect("Timeframes", list(timeframe_dict.keys()), default=["1 Hour"])
col1, col2 = st.columns(2)
with col1: selected_bases = st.multiselect("Base Candles", [1, 2, 3], default=[1, 2])
with col2: selected_legouts = st.multiselect("Legout Count", [1, 2, 3], default=[1])

if st.button("🚀 SCAN"):
    all_zones = []
    for tf_label in selected_tf:
        data = yf.Ticker(selected_symbol).history(period="60d", interval=timeframe_dict[tf_label])
        zones = scan_zones(data, selected_symbol, tf_label, selected_bases, selected_legouts)
        all_zones.extend(zones)
    
    master_df = pd.DataFrame(all_zones)
    st.dataframe(master_df)
    
    if st.button("📢 Send Alerts for Fresh Zones"):
        for _, row in master_df[master_df['Status'] == 'FRESH'].iterrows():
            msg = f"🟢 *NEW ZONE*\nSymbol: {row['Symbol']}\nType: {row['Type']}\nProximal: {row['Proximal']}"
            send_telegram_alert(market_cat, msg)
        st.success("Alerts Sent!")
