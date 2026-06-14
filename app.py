import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide", page_title="Institutional Supply/Demand Matrix Scanner")
st.markdown("<h1 style='text-align: center; color: #2ecc71;'>⚡ Institutional Supply & Demand Matrix Scanner</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------------------------
# ⚙️ MULTI-CHANNEL TELEGRAM CONFIGURATION
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN"
CHANNEL_IDS = {
    "Indian Stocks (Nifty 100)": "YAHAN_NIFTY_CHANNEL_CHAT_ID_DALEIN",
    "US Stocks (Nasdaq 100)": "YAHAN_US_STOCKS_CHANNEL_CHAT_ID_DALEIN",
    "Forex (Majors, Minors & Crosses)": "YAHAN_FOREX_COMMODITY_CHANNEL_CHAT_ID_DALEIN",
    "Commodities": "YAHAN_FOREX_COMMODITY_CHANNEL_CHAT_ID_DALEIN",
    "Crypto": "YAHAN_CRYPTO_CHANNEL_CHAT_ID_DALEIN"
}

def send_market_specific_alert(category, message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN": return
    target_id = CHANNEL_IDS.get(category, CHANNEL_IDS["Forex (Majors, Minors & Crosses)"])
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": target_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception:
        pass

# -------------------------------------------------------------------
# MASTER DATABASE
# -------------------------------------------------------------------
def get_complete_asset_database():
    return {
        "Indian Stocks (Nifty 100)": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
        "US Stocks (Nasdaq 100)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"],
        "Forex (Majors, Minors & Crosses)": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"],
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
        "Commodities": ["GC=F", "CL=F", "NG=F"]
    }

assets_master = get_complete_asset_database()

def resample_data(df, timeframe_str):
    if df.empty or timeframe_str in ['5m', '15m', '30m', '1h', '1d', '1wk']: return df
    df = df.copy()
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    resample_map = {"45m": "45min", "75m": "75min", "125m": "125min", "2h": "2h", "4h": "4h"}
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
            
            legin, legout = df.iloc[legin_idx], df.iloc[legout_idx]
            bases = df.iloc[base_indices]
            
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: continue
            if legout['body_size'] <= legin['body_size']: continue
                
            legout_count = 1
            direction_green = legout['is_green']
            for k in range(legout_idx + 1, len(df)):
                if df.iloc[k]['is_green'] == direction_green and df.iloc[k]['body_ratio'] >= 50: legout_count += 1
                else: break
                    
            legin_green, legout_green = legin['is_green'], legout['is_green']
            pattern, z_type, proximal, distal = None, None, 0.0, 0.0
            
            if legin_green and legout_green: pattern, z_type = "RBR", "Demand"
            elif legin_green and not legout_green: pattern, z_type = "RBD", "Supply"
            elif not legin_green and legout_green: pattern, z_type = "DBR", "Demand"
            elif not legin_green and not legout_green: pattern, z_type = "DBD", "Supply"
                
            zone_size = abs(proximal - distal)
            if z_type == "Demand":
                proximal, distal = bases['High'].max(), bases['Low'].min()
                target_price = proximal + (abs(proximal - distal) * 2)
            else:
                proximal, distal = bases['Low'].min(), bases['High'].max()
                target_price = proximal - (abs(proximal - distal) * 2)
                
            status = "FRESH"
            entered_zone = False
            for j in range(legout_idx + 1, len(df)):
                cl, ch = df.iloc[j]['Low'], df.iloc[j]['High']
                if z_type == "Demand":
                    if cl <= proximal: entered_zone = True
                    if entered_zone:
                        if cl < distal: status = "SL HIT"; break
                        elif ch >= target_price: status = "TARGET"; break
                else:
                    if ch >= proximal: entered_zone = True
                    if entered_zone:
                        if ch > distal: status = "SL HIT"; break
                        elif cl <= target_price: status = "TARGET"; break
                            
            zones.append({
                "Symbol": symbol_name, "Timeframe": tf_name, "Pattern": pattern, "Type": z_type,
                "Proximal": round(proximal, 4), "Distal": round(distal, 4), "Target (1:2)": round(target_price, 4),
                "Status": status, "Base Count": num_base, "Legout Count": legout_count,
                "Formed At": df.index[i].strftime('%Y-%m-%d %H:%M')
            })
    return zones

# CONTROL PANEL
st.markdown("### 🎛️ Scanner Control Matrix")
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    market_cat = st.selectbox("1. Choose Market Category", list(assets_master.keys()))
with row1_col2:
    selected_symbol_raw = st.selectbox("2. Select Target Ticker List", ["🎨 [ALL SYMBOLS]"] + assets_master[market_cat])

row2_col1, row2_col2 = st.columns(2)
timeframe_dictionary = {"1 Hour": "1h", "4 Hour": "4h", "Daily": "1d"}
with row2_col1:
    selected_tf_labels = st.multiselect("3. Select Timeframes", list(timeframe_dictionary.keys()), default=["1 Hour"])
with row2_col2:
    zone_filter_mode = st.radio("4. Integrity Condition", ["FRESH", "SL HIT", "TARGET", "ALL"], horizontal=True)

send_alerts = st.checkbox("📢 Send Fresh Zones to Segregated Telegram Channels", value=True)
run_scan_btn = st.button("🚀 START STRUCTURAL MATRIX SCAN", use_container_width=True)

if run_scan_btn:
    target_symbols = assets_master[market_cat] if selected_symbol_raw == "🎨 [ALL SYMBOLS]" else [selected_symbol_raw]
    all_detected_zones = []
    
    with st.spinner("Analyzing Matrix streams..."):
        for symbol in target_symbols:
            for tf_label in selected_tf_labels:
                tf_code = timeframe_dictionary[tf_label]
                try:
                    raw_feed = yf.Ticker(symbol).history(period="360d" if tf_code=="1h" else "5y", interval="1h" if tf_code != "1d" else "1d")
                    if raw_feed.empty: continue
                    processed_feed = resample_data(raw_feed, tf_code)
                    all_detected_zones.extend(scan_supply_demand_zones(processed_feed, symbol, tf_label))
                except Exception: continue

    if all_detected_zones:
        master_df = pd.DataFrame(all_detected_zones)
        total_fresh = len(master_df[master_df["Status"] == "FRESH"])
        total_target = len(master_df[master_df["Status"] == "TARGET"])
        total_sl_hit = len(master_df[master_df["Status"] == "SL HIT"])
        
        if zone_filter_mode != "ALL":
            master_df = master_df[master_df["Status"] == zone_filter_mode]
            
        st.success(f"📊 Scan Completed! Found {len(master_df)} matching points.")
        
        # Broadcast Manual Scans to exact channels
        if send_alerts and not master_df.empty:
            fresh_only_df = master_df[master_df["Status"] == "FRESH"]
            for _, alert_row in fresh_only_df.iterrows():
                emoji = "🟢" if alert_row['Type'] == "Demand" else "🔴"
                alert_msg = f"{emoji} *MANUAL NEW ZONE* {emoji}\n\n▪️ *SYMBOL :* `{alert_row['Symbol']}`\n▪️ *TIMEFRAME :* `{alert_row['Timeframe']}`\n▪️ *PROXIMAL :* `{alert_row['Proximal']}`\n▪️ *TARGET (1:2) :* `{alert_row['Target (1:2)']}`"
                send_market_specific_alert(market_cat, alert_msg)
            st.info("📢 Segmented notifications dispatched successfully!")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scanned", f"{len(target_symbols)}A")
        m2.metric("🟢 Fresh", total_fresh)
        m3.metric("🎯 Targets", total_target)
        m4.metric("🔴 SL Hits", total_sl_hit)
        
        st.dataframe(master_df.sort_values(by="Formed At", ascending=False), use_container_width=True)
