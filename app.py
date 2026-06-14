import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests

# Full Screen Configuration
st.set_page_config(layout="wide", page_title="Institutional Supply/Demand Matrix Scanner")

# Centered Title Layout
st.markdown("<h1 style='text-align: center; color: #2ecc71;'>⚡ Institutional Supply & Demand Matrix Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #bdc3c7;'>Multi-Asset, Multi-Timeframe Institutional Cluster Intelligence System with Premium Alerts</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------------------------
# ⚙️ TELEGRAM CONFIGURATION (Apna Token aur Chat ID Yahan Dalein)
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN"  # <-- Apne bot ka token yahan dalein
TELEGRAM_CHAT_ID = "YAHAN_APNI_CHAT_ID_PASTE_KAREIN"  # <-- Chat ID daalna na bhulein

def send_telegram_alert(message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN" or TELEGRAM_CHAT_ID == "YAHAN_APNI_CHAT_ID_PASTE_KAREIN":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        pass

# -------------------------------------------------------------------
# 1. COMPLETE ASSETS MASTER DATABASE
# -------------------------------------------------------------------
def get_complete_asset_database():
    return {
        "Indian Stocks (Nifty 100)": [
            "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS",
            "ASIANPAINT.NS", "ASTRAL.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS",
            "BERGEPAINT.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BOSCHLTD.NS", "BRITANNIA.NS", "CANBK.NS", "CGPOWER.NS",
            "CHOLAMAND.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "CUMMINSIND.NS", "DLF.NS", "DABUR.NS", "DIVISLAB.NS",
            "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS", "GMRINFRA.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HAL.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "ITC.NS",
            "INDIANB.NS", "INDHOTEL.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS", "INFY.NS", "INTERGLOBE.NS",
            "JINDALSTEL.NS", "JIOFIN.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KPITTECH.NS", "KOTAKBANK.NS", "L&TFH.NS", "LT.NS", "LTIM.NS", "LICHSGFIN.NS",
            "LUPIN.NS", "M&M.NS", "MARICO.NS", "MARUTI.NS", "MAXHEALTH.NS", "NTPC.NS", "NESTLEIND.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS",
            "PIIND.NS", "PFC.NS", "POWERGRID.NS", "PNB.NS", "RELIANCE.NS", "SBICARD.NS", "SBILIFE.NS", "SRF.NS", "MOTHERSON.NS", "SHREECEM.NS",
            "SHRIRAMFIN.NS", "SIEMENS.NS", "SONACOMS.NS", "SBIN.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUPREMEIND.NS", "SUZLON.NS", "TATACOMM.NS", "TATACONSUM.NS",
            "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TRENT.NS", "TIINDIA.NS",
            "UPL.NS", "ULTRACEMCO.NS", "UNITDSPR.NS", "VBL.NS", "VEDL.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZOMATO.NS"
        ],
        "US Stocks (Nasdaq 100)": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP", "COST",
            "CSCO", "TMUS", "ADBE", "NFLX", "AMD", "CMCSA", "TXN", "QCOM", "INTC", "AMGN"
        ],
        "Forex (Majors, Minors & Crosses)": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURCAD=X", "EURCHF=X", "GBPCAD=X"
        ],
        "Crypto": [
            "BTC-USD", "ETH-USD", "SOL-USD"
        ],
        "Commodities": [
            "GC=F", "SI=F", "HG=F", "ZN=F", "CL=F", "NG=F"
        ]
    }

assets_master = get_complete_asset_database()

# -------------------------------------------------------------------
# RESAMPLING ENGINE
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# ADVANCED S&D CORE SCANNING ENGINE (Optimized for 1:2 RR Target)
# -------------------------------------------------------------------
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
            
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60: continue
            
            valid_bases = True
            for _, base in bases.iterrows():
                if base['body_size'] > (legin['body_size'] * 0.5):
                    valid_bases = False
                    break
            if not valid_bases: continue
            if legout['body_size'] <= legin['body_size']: continue
                
            legout_count = 1
            direction_green = legout['is_green']
            for k in range(legout_idx + 1, len(df)):
                if df.iloc[k]['is_green'] == direction_green and df.iloc[k]['body_ratio'] >= 50:
                    legout_count += 1
                else:
                    break
                    
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
                
            # 🔥 CHANGED TO 1:2 RISK TO REWARD
            zone_size = abs(proximal - distal)
            if z_type == "Demand":
                target_price = proximal + (zone_size * 2)
            else:
                target_price = proximal - (zone_size * 2)

            # Integrity checking
            status = "FRESH"
            entered_zone = False
            
            for j in range(legout_idx + 1, len(df)):
                current_low = df.iloc[j]['Low']
                current_high = df.iloc[j]['High']
                
                if z_type == "Demand":
                    if current_low <= proximal:
                        entered_zone = True
                    if entered_zone:
                        if current_low < distal:
                            status = "SL HIT"
                            break
                        elif current_high >= target_price:
                            status = "TARGET"
                            break
                else: # Supply
                    if current_high >= proximal:
                        entered_zone = True
                    if entered_zone:
                        if current_high > distal:
                            status = "SL HIT"
                            break
                        elif current_low <= target_price:
                            status = "TARGET"
                            break
                            
            zones.append({
                "Symbol": symbol_name, "Timeframe": tf_name, "Pattern": pattern, "Type": z_type,
                "Proximal": round(proximal, 4), "Distal": round(distal, 4), "Target (1:2)": round(target_price, 4),
                "Status": status, "Base Count": num_base, "Legout Count": legout_count,
                "Formed At": df.index[i].strftime('%Y-%m-%d %H:%M')
            })
    return zones

# -------------------------------------------------------------------
# MAIN CONTROL PANEL LAYOUT
# -------------------------------------------------------------------
st.markdown("### 🎛️ Scanner Control Matrix")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    market_cat = st.selectbox("1. Choose Market Category", list(assets_master.keys()))
with row1_col2:
    symbols_options = ["🎨 [ALL SYMBOLS]"] + assets_master[market_cat]
    selected_symbol_raw = st.selectbox("2. Select Target Ticker / Pair List", symbols_options)

row2_col1, row2_col2 = st.columns(2)
timeframe_dictionary = {
    "5 Min": "5m", "15 Min": "15m", "30 Min": "30m", "45 Min": "45m", "75 Min": "75m", "125 Min": "125m",
    "1 Hour": "1h", "2 Hour": "2h", "4 Hour": "4h", "5 Hour": "5h", "6 Hour": "6h", "8 Hour": "8h",
    "10 Hour": "10h", "16 Hour": "16h", "Daily": "1d", "Weekly": "1wk"
}

with row2_col1:
    selected_tf_labels = st.multiselect("3. Select Timeframes", list(timeframe_dictionary.keys()), default=["1 Hour"])
with row2_col2:
    zone_filter_mode = st.radio("4. Target Zone Integrity Condition", ["FRESH", "SL HIT", "TARGET", "ALL"], horizontal=True)

st.markdown("##### 🔍 Quick External Ticker Override")
quick_search = st.text_input("Type any unique global asset symbol (e.g., GOOG, TCS.NS, ETH-USD):", "").strip()

send_alerts = st.checkbox("📢 Send Fresh Zones to Telegram Channel/Bot", value=True)

st.markdown("<br>", unsafe_allow_html=True)
run_scan_btn = st.button("🚀 START STRUCTURAL MATRIX SCAN", use_container_width=True)
st.markdown("---")

# -------------------------------------------------------------------
# EXECUTION ENGINE PIPELINE
# -------------------------------------------------------------------
if run_scan_btn:
    if quick_search: target_symbols = [quick_search]
    elif selected_symbol_raw == "🎨 [ALL SYMBOLS]": target_symbols = assets_master[market_cat]
    else: target_symbols = [selected_symbol_raw]
        
    all_detected_zones = []
    
    with st.spinner("Executing structural wave analysis over data streams..."):
        for symbol in target_symbols:
            for tf_label in selected_tf_labels:
                tf_code = timeframe_dictionary[tf_label]
                
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
                    zone_logs = scan_supply_demand_zones(processed_feed, symbol, tf_label)
                    all_detected_zones.extend(zone_logs)
                except Exception:
                    continue

    if all_detected_zones:
        master_df = pd.DataFrame(all_detected_zones)
        
        # Calculations for Metrics Panel
        total_fresh = len(master_df[master_df["Status"] == "FRESH"])
        total_target = len(master_df[master_df["Status"] == "TARGET"])
        total_sl_hit = len(master_df[master_df["Status"] == "SL HIT"])
        
        if zone_filter_mode != "ALL":
            master_df = master_df[master_df["Status"] == zone_filter_mode]
            
        st.success(f"📊 Matrix Sweep Completed! Found {len(master_df)} matching structure points.")
        
        # Telegram Alerts for Fresh Zones
        if send_alerts and not master_df.empty:
            fresh_only_df = master_df[master_df["Status"] == "FRESH"]
            if not fresh_only_df.empty:
                for _, alert_row in fresh_only_df.iterrows():
                    emoji = "🟢" if alert_row['Type'] == "Demand" else "🔴"
                    alert_msg = (
                        f"{emoji} *NEW ZONE DETECTED* {emoji}\n\n"
                        f"▪️ *SYMBOL :* `{alert_row['Symbol']}`\n"
                        f"▪️ *TIMEFRAME :* `{alert_row['Timeframe']}`\n"
                        f"▪️ *PATTERN :* `{alert_row['Pattern']}`\n"
                        f"▪️ *TYPE :* `{alert_row['Type'].upper()}`\n"
                        f"▪️ *BASE COUNT :* `{alert_row['Base Count']}`\n"
                        f"▪️ *LEGOUT COUNT :* `{alert_row['Legout Count']}`\n"
                        f"▪️ *STATUS :* `{alert_row['Status']}`\n"
                        f"▪️ *PROXIMAL LINE :* `{alert_row['Proximal']}`\n"
                        f"▪️ *DISTAL LINE :* `{alert_row['Distal']}`\n"
                        f"▪️ *DATE OF ZONE FORMED :* `{alert_row['Formed At']}`\n\n"
                        f"📈 _Scanner powered by Global Bot System_"
                    )
                    send_telegram_alert(alert_msg)
                st.info("📢 Fresh zones have been broadcasted to your Telegram Bot successfully!")

        # Metrics Panel Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scanned Combos", f"{len(target_symbols)}A x {len(selected_tf_labels)}TFs")
        m2.metric("🟢 Fresh Active Zones", total_fresh)
        m3.metric("🎯 Target Hits (1:2 RR)", total_target)
        m4.metric("🔴 Stop Loss (SL) Hits", total_sl_hit)
        
        # Clean Columns Mapping with new Target (1:2)
        clean_columns = ["Symbol", "Timeframe", "Pattern", "Type", "Base Count", "Legout Count", "Status", "Proximal", "Distal", "Target (1:2)", "Formed At"]
        master_df = master_df[clean_columns]
        
        st.subheader("📋 Core Structural Database Logs")
        st.dataframe(master_df.sort_values(by="Formed At", ascending=False), use_container_width=True)
        
        # Plotly Visual Grid System
        st.markdown("### 🔍 Live Visual Chart Matrix (Click Expand to View Chart)")
        
        for idx, row in master_df.sort_values(by="Formed At", ascending=False).iterrows():
            status_emoji = "🟢 Demand" if row['Type'] == "Demand" else "🔴 Supply"
            expander_title = f"📈 {row['Symbol']} | {row['Timeframe']} | {row['Pattern']} | Status: {row['Status']} | formed at {row['Formed At']}"
            
            with st.expander(expander_title):
                curr_tf_code = timeframe_dictionary[row['Timeframe']]
                if curr_tf_code in ["5m", "15m", "30m", "45m", "75m", "125m"]: last_fetch, last_period = "5m", "59d"
                elif curr_tf_code in ["1h", "2h", "4h", "5h", "6h", "8h", "10h", "16h"]: last_fetch, last_period = "1h", "360d"
                else: last_fetch, last_period = "1d", "5y"
                
                try:
                    chart_feed = resample_data(yf.Ticker(row['Symbol']).history(period=last_period, interval=last_fetch), curr_tf_code)
                    
                    if not chart_feed.empty:
                        fig = go.Figure(data=[go.Candlestick(
                            x=chart_feed.index, open=chart_feed['Open'], high=chart_feed['High'], 
                            low=chart_feed['Low'], close=chart_feed['Close'], name="Price Feed"
                        )])
                        
                        shape_color = "rgba(46, 204, 113, 0.15)" if row['Type'] == "Demand" else "rgba(231, 76, 60, 0.15)"
                        line_color = "#2ecc71" if row['Type'] == "Demand" else "#e74c3c"
                        
                        # Draw Zone Shape Block
                        fig.add_shape(
                            type="rect", x0=row['Formed At'], y0=row['Distal'], x1=chart_feed.index[-1], y1=row['Proximal'],
                            fillcolor=shape_color, line=dict(color=line_color, width=1)
                        )
                        
                        # Draw 1:2 Target Line (Blue Dashed)
                        fig.add_shape(
                            type="line", x0=row['Formed At'], y0=row['Target (1:2)'], x1=chart_feed.index[-1], y1=row['Target (1:2)'],
                            line=dict(color="#3498db", width=2, dash="dash"), name="Target (1:2)"
                        )
                        
                        fig.update_layout(
                            title=f"{row['Symbol']} {row['Timeframe']} - Institutional Map (Target 1:2 Line Marked In Blue)",
                            template="plotly_dark", height=450, xaxis_rangeslider_visible=False,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{row['Symbol']}_{idx}")
                    else:
                        st.error("Could not render data matrix for this ticker.")
                except Exception as chart_err:
                    st.error(f"Chart Render Error: {chart_err}")
    else:
        st.info("No corporate structural clusters detected matching the filter rules with current pipeline settings.")
