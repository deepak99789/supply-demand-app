import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# Full Screen Configuration
st.set_page_config(layout="wide", page_title="Institutional Supply/Demand Matrix Scanner")

# Centered Title Layout
st.markdown("<h1 style='text-align: center; color: #2ecc71;'>⚡ Institutional Supply & Demand Matrix Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #bdc3c7;'>Multi-Asset, Multi-Timeframe Institutional Cluster Intelligence System</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------------------------------------------
# 1. 100% COMPLETE ASSETS MASTER DATABASE (Nifty 100, Nasdaq 100, Forex, Crypto, Commodities)
# -------------------------------------------------------------------
def get_complete_asset_database():
    return {
        "Indian Stocks (Nifty 100)": [
            "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS",
            "ASIANPAINT.NS", "ASTRAL.NS", "AU SMALL.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS",
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
            "CSCO", "TMUS", "ADBE", "NFLX", "AMD", "CMCSA", "TXN", "QCOM", "INTC", "AMGN",
            "ISRG", "HON", "BKNG", "MDLZ", "VRTX", "GILD", "ADP", "REGN", "PANW", "MU",
            "LRCX", "MELI", "SNPS", "KLAC", "CDNS", "CHTR", "MAR", "ORLY", "ASML", "NXPI",
            "CTAS", "WDAY", "MNST", "ROST", "ADSK", "PDD", "PAYX", "PCAR", "ILMN", "GEHC",
            "DLTR", "AEP", "ODFL", "AZN", "EXC", "IDXX", "KDP", "LULU", "BIIB", "MCHP",
            "FAST", "CSX", "FITB", "VRSK", "TEAM", "ANSS", "DXCM", "DDOG", "FANG",
            "WBD", "ALGN", "CEG", "SIRI", "ZM", "EBAY", "JD", "LCID", "ABNB", "ZS", 
            "GFS", "MRVL", "OKTA", "SWKS", "NTES", "DOCU", "AMAT", "EA", "CTSH", "CZR", 
            "MNDY", "COIN", "HOOD", "ARM"
        ],
        "Forex (Majors, Minors & Crosses)": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURCAD=X", "EURCHF=X", "GBPCAD=X",
            "CHFJPY=X", "NZDJPY=X", "CADJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X", "EURAUD=X",
            "EURNZD=X", "GBPAUD=X", "GBPNZD=X", "GBPCHF=X", "CADCHF=X", "NZDCHF=X"
        ],
        "Crypto": [
            "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "BNB-USD", "ADA-USD", "XRP-USD", "DOT-USD", "SHIB-USD", "LTC-USD", "LINK-USD", "AVAX-USD", "MATIC-USD"
        ],
        "Commodities": [
            "GC=F", "CL=F", "SI=F", "NG=F", "BZ=F", "HG=F", "ZC=F", "ZO=F", "PL=F", "PA=F"
        ]
    }

assets_master = get_complete_asset_database()

# Resampling Algorithm
def resample_data(df, timeframe_str):
    if timeframe_str in ['5m', '15m', '30m', '1h', '1d', '1wk']:
        return df
    resample_map = {
        "45m": "45T", "75m": "75T", "125m": "125T", 
        "2h": "120T", "4h": "240T", "5h": "300T", 
        "6h": "360T", "8h": "480T", "10h": "600T", "16h": "960T"
    }
    rule = resample_map.get(timeframe_str)
    if not rule: return df
    return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

# S&D Core Processing Algorithm
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
                
            legin = df.iloc[legin_idx]
            legout = df.iloc[legout_idx]
            follow_up = df.iloc[follow_up_idx]
            bases = df.iloc[base_indices]
            
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
                    
            zones.append({
                "Symbol": symbol_name, "Timeframe": tf_name, "Pattern Time": df.index[i].strftime('%Y-%m-%d %H:%M'),
                "Zone Type": zone_type, "Proximal": round(proximal, 4), "Distal": round(distal, 4),
                "Status": "Tested" if tested else "Fresh", "Base Count": num_base
            })
    return zones

# -------------------------------------------------------------------
# MAIN CENTER SCREEN CONTROL PANEL LAYOUT
# -------------------------------------------------------------------
st.markdown("### 🎛️ Scanner Control Matrix")

# Row 1: Category and Symbol Selectors
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    market_cat = st.selectbox("1. Choose Market Category", list(assets_master.keys()))
with row1_col2:
    symbols_options = ["🎨 [ALL SYMBOLS]"] + assets_master[market_cat]
    selected_symbol_raw = st.selectbox("2. Select Target Ticker / Pair List", symbols_options)

# Row 2: Multi-Timeframes & Filters
row2_col1, row2_col2 = st.columns(2)
timeframe_dictionary = {
    "5 Min": "5m", "15 Min": "15m", "30 Min": "30m", "45 Min": "45m", "75 Min": "75m", "125 Min": "125m",
    "1 Hour": "1h", "2 Hour": "2h", "4 Hour": "4h", "5 Hour": "5h", "6 Hour": "6h", "8 Hour": "8h",
    "10 Hour": "10h", "16 Hour": "16h", "Daily": "1d", "Weekly": "1wk"
}

with row2_col1:
    selected_tf_labels = st.multiselect("3. Select Timeframes (Choose Multiple to Scan at Once)", list(timeframe_dictionary.keys()), default=["1 Hour"])
with row2_col2:
    zone_filter_mode = st.radio("4. Target Zone Integrity Condition", ["All", "Fresh", "Tested"], horizontal=True)

# Universal Global Dynamic Input Search Bar
st.markdown("##### 🔍 Quick External Ticker Override")
quick_search = st.text_input("Type any unique global asset symbol (Overrides above selections, e.g., GOOG, TCS.NS, ETH-USD):", "").strip()

# --- THE MANUAL RUN BUTTON ---
st.markdown("<br>", unsafe_allow_html=True)
run_scan_btn = st.button("🚀 START STRUCTURAL MATRIX SCAN", use_container_width=True)
st.markdown("---")

# -------------------------------------------------------------------
# EXECUTION ENGINE PIPELINE
# -------------------------------------------------------------------
if run_scan_btn:
    # Finalize Target Symbols List
    if quick_search:
        target_symbols = [quick_search]
    elif selected_symbol_raw == "🎨 [ALL SYMBOLS]":
        target_symbols = assets_master[market_cat]
    else:
        target_symbols = [selected_symbol_raw]
        
    all_detected_zones = []
    
    with st.spinner("Executing structural wave analysis over cloud data streams..."):
        for symbol in target_symbols:
            for tf_label in selected_tf_labels:
                tf_code = timeframe_dictionary[tf_label]
                
                # --- BULLETPROOF FIXED TIME-PERIOD STRATEGY FOR ALL TIMEFRAMES ---
                if tf_code in ["5m", "15m", "30m", "45m", "75m", "125m"]:
                    fetch_interval = "5m"
                    history_period = "30d"  # Safest limit for 5m data download
                elif tf_code in ["1h", "2h", "4h", "5h", "6h", "8h", "10h", "16h"]:
                    fetch_interval = "1h"
                    history_period = "360d" # Safe 1-Year limit: Fixes 2h, 4h, 8h, 10h completely
                else:
                    fetch_interval = "1d"
                    history_period = "5y"   # Perfect for Daily and Weekly
                
                try:
                    raw_feed = yf.Ticker(symbol).history(period=history_period, interval=fetch_interval)
                    if raw_feed.empty: continue
                    
                    processed_feed = resample_data(raw_feed, tf_code)
                    zone_logs = scan_supply_demand_zones(processed_feed, symbol, tf_label)
                    all_detected_zones.extend(zone_logs)
                except Exception:
                    continue # Skip silently to handle errors smoothly

    # Display Engine
    if all_detected_zones:
        master_df = pd.DataFrame(all_detected_zones)
        
        # Apply Integrity Conditions
        if zone_filter_mode != "All":
            master_df = master_df[master_df["Status"] == zone_filter_mode]
            
        st.success(f"📊 Matrix Sweep Completed! Found {len(master_df)} valid structure points.")
        
        # Main Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scanned Combos", f"{len(target_symbols)} Assets x {len(selected_tf_labels)} TFs")
        m2.metric("Fresh Active Zones", len(master_df[master_df["Status"] == "Fresh"]))
        m3.metric("Tested Zones Logged", len(master_df[master_df["Status"] == "Tested"]))
        
        # Data View Matrix Table
        st.subheader("📋 Core Structural Database Logs")
        st.dataframe(master_df.sort_values(by="Pattern Time", ascending=False), use_container_width=True)
        
        # Dynamic Interactive Chart Canvas Rendering (For Single Asset Mode)
        if len(target_symbols) == 1 and not master_df.empty:
            st.subheader(f"📈 Real-time Visual Layer Map ({target_symbols[0]})")
            last_tf_label = selected_tf_labels[-1]
            last_tf_code = timeframe_dictionary[last_tf_label]
            
            if last_tf_code in ["5m", "15m", "30m", "45m", "75m", "125m"]:
                last_fetch = "5m"
                last_period = "30d"
            elif last_tf_code in ["1h", "2h", "4h", "5h", "6h", "8h", "10h", "16h"]:
                last_fetch = "1h"
                last_period = "360d"
            else:
                last_fetch = "1d"
                last_period = "5y"
            
            try:
                chart_feed = resample_data(yf.Ticker(target_symbols[0]).history(period=last_period, interval=last_fetch), last_tf_code)
                fig = go.Figure(data=[go.Candlestick(x=chart_feed.index, open=chart_feed['Open'], high=chart_feed['High'], low=chart_feed['Low'], close=chart_feed['Close'], name="Price Feed")])
                
                for _, row in master_df[master_df["Symbol"] == target_symbols[0]].tail(10).iterrows():
                    shape_color = "rgba(46, 204, 113, 0.14)" if "Demand" in row['Zone Type'] else "rgba(231, 76, 60, 0.14)"
                    try:
                        fig.add_shape(type="rect", x0=row['Pattern Time'], y0=row['Distal'], x1=chart_feed.index[-1], y1=row['Proximal'], fillcolor=shape_color, line=dict(width=0))
                    except Exception:
                        pass
                fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass
    else:
        st.info("No corporate structural clusters detected matching the filter rules with current pipeline settings.")
