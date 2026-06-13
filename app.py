import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="Ultimate Supply/Demand Scanner")
st.title("⚡ Pro Supply & Demand Scanner (Custom Timeframes)")
st.markdown("---")

# 1. Complete Asset Lists (Nifty 100, Nasdaq 100, Forex, Crypto, Commodities)
def get_asset_lists():
    return {
        "Indian Stocks (Nifty 100)": [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS",
            "BAJAJFINSV.NS", "RELIANCE.NS", "AXISBANK.NS", "LT.NS", "KOTAKBANK.NS", "HCLTECH.NS", "M&M.NS", "SUNPHARMA.NS", "MARUTI.NS", "NTPC.NS",
            "TATAMOTORS.NS", "ONGC.NS", "ADANIENT.NS", "COALINDIA.NS", "JIOFIN.NS", "JSWSTEEL.NS", "HINDALCO.NS", "TATASTEEL.NS", "GRASIM.NS", "POWERGRID.NS"
        ],
        "US Stocks (Nasdaq 100)": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "PEP", "COST", "AVGO",
            "CSCO", "TMUS", "ADBE", "NFLX", "AMD", "CMCSA", "TXN", "QCOM", "INTC", "HON",
            "AMGN", "ISRG", "BKNG", "MDLZ", "VRTX", "GILD", "REGN", "ADP", "PANW", "MU"
        ],
        "Forex (Major/Minor/Cross)": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURCAD=X", "EURCHF=X", "GBPCAD=X"
        ],
        "Crypto": [
            "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "BNB-USD", "ADA-USD", "XRP-USD", "DOT-USD", "SHIB-USD", "LTC-USD"
        ],
        "Commodities": [
            "GC=F", "CL=F", "SI=F", "NG=F", "BZ=F", "HG=F", "ZC=F", "ZO=F"
        ]
    }

assets_dict = get_asset_lists()

# 2. Resampling Engine for Custom Timeframes
def resample_data(df, timeframe_str):
    if timeframe_str in ['5m', '15m', '30m', '1h', '1d', '1wk']:
        return df
        
    resample_map = {
        "45m": "45T", "75m": "75T", "125m": "125T", 
        "2h": "120T", "4h": "240T", "5h": "300T", 
        "6h": "360T", "8h": "480T", "10h": "600T", "16h": "960T"
    }
    
    rule = resample_map.get(timeframe_str)
    if not rule:
        return df
        
    resampled = df.resample(rule).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    return resampled

# 3. Supply & Demand Zone Core Algorithm
def identify_zones(df):
    zones = []
    if len(df) < 10:
        return pd.DataFrame()
        
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
            
            if follow_up_idx >= len(df):
                continue
                
            legin = df.iloc[legin_idx]
            legout = df.iloc[legout_idx]
            follow_up = df.iloc[follow_up_idx]
            bases = df.iloc[base_indices]
            
            # Condition 1: Explosive Check (>60% Body)
            if legin['body_ratio'] < 60 or legout['body_ratio'] < 60:
                continue
                
            # Condition 2: Base Candle Body <= 50% of Legin Body
            valid_bases = True
            for _, base in bases.iterrows():
                if base['body_size'] > (legin['body_size'] * 0.5):
                    valid_bases = False
                    break
            if not valid_bases:
                continue
                
            # Condition 3: Legout Body Size > Legin Body Size & Same color Follow-up
            if legout['body_size'] <= legin['body_size']:
                continue
            if legout['is_green'] != follow_up['is_green']:
                continue
                
            # Zone Strategy Mapping
            legin_green = legin['is_green']
            legout_green = legout['is_green']
            zone_type, proximal, distal = None, 0.0, 0.0
            
            if legin_green and legout_green:
                zone_type = "RBR (Rally-Base-Rally) - Demand"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif legin_green and not legout_green:
                zone_type = "RBD (Rally-Base-Drop) - Supply"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
            elif not legin_green and legout_green:
                zone_type = "DBR (Drop-Base-Rally) - Demand"
                proximal = bases['High'].max()
                distal = bases['Low'].min()
            elif not legin_green and not legout_green:
                zone_type = "DBD (Drop-Base-Drop) - Supply"
                proximal = bases['Low'].min()
                distal = bases['High'].max()
                
            # Fresh vs Tested Scanning Engine
            tested = False
            for j in range(follow_up_idx + 1, len(df)):
                if "Demand" in zone_type and df.iloc[j]['Low'] <= proximal:
                    tested = True
                    break
                if "Supply" in zone_type and df.iloc[j]['High'] >= proximal:
                    tested = True
                    break
                    
            zones.append({
                "Time": df.index[i].strftime('%Y-%m-%d %H:%M'),
                "Type": zone_type,
                "Proximal": round(proximal, 4),
                "Distal": round(distal, 4),
                "Status": "Tested" if tested else "Fresh",
                "Base Candles": num_base
            })
            
    return pd.DataFrame(zones)

# Sidebar Configuration
st.sidebar.header("🛠️ System Configuration")
market_type = st.sidebar.selectbox("Market Category", list(assets_dict.keys()))
selected_symbol = st.sidebar.selectbox("Select Symbol from List", assets_dict[market_type])

timeframe_opts = {
    "5 Min": "5m", "15 Min": "15m", "30 Min": "30m", "45 Min": "45m",
    "75 Min": "75m", "125 Min": "125m", "1 Hour": "1h", "2 Hour": "2h",
    "4 Hour": "4h", "5 Hour": "5h", "6 Hour": "6h", "8 Hour": "8h",
    "10 Hour": "10h", "16 Hour": "16h", "Daily": "1d", "Weekly": "1wk"
}
selected_tf_label = st.sidebar.selectbox("Select Timeframe", list(timeframe_opts.keys()))
selected_tf = timeframe_opts[selected_tf_label]
zone_filter = st.sidebar.radio("Zone Filter Mode", ["All", "Fresh", "Tested"])

# Global Search Bar on Main Screen
st.subheader("🔍 Universal Asset Search")
search_query = st.text_input("Directly input any Ticker Symbol (eg: SBIN.NS, AAPL, BTC-USD, GC=F):", value=selected_symbol)
active_symbol = search_query.strip() if search_query else selected_symbol

if active_symbol:
    with st.spinner(f"Fetching market feed and scanning structural zones for {active_symbol}..."):
        try:
            # Smart period strategy based on timeframe requirements
            if selected_tf in ["5m", "15m", "30m", "45m", "75m", "125m"]:
                fetch_tf = "5m"
                period = "60d"
            elif selected_tf in ["1h", "2h", "4h", "5h", "6h", "8h", "10h", "16h"]:
                fetch_tf = "1h"
                period = "730d"
            else:
                fetch_tf = selected_tf
                period = "5y"
                
            df_raw = yf.Ticker(active_symbol).history(period=period, interval=fetch_tf)
            
            if not df_raw.empty:
                df_processed = resample_data(df_raw, selected_tf)
                zones_df = identify_zones(df_processed)
                
                if zone_filter != "All" and not zones_df.empty:
                    zones_df = zones_df[zones_df["Status"] == zone_filter]
                    
                # Technical Dashboard Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Candlesticks Scanned", len(df_processed))
                if not zones_df.empty:
                    c2.metric("Total Fresh Zones Active", len(zones_df[zones_df["Status"] == "Fresh"]))
                    c3.metric("Total Tested Zones Active", len(zones_df[zones_df["Status"] == "Tested"]))
                else:
                    c2.metric("Total Fresh Zones Active", 0)
                    c3.metric("Total Tested Zones Active", 0)

                # Plotly Chart Interface
                fig = go.Figure(data=[go.Candlestick(
                    x=df_processed.index, 
                    open=df_processed['Open'], high=df_processed['High'], 
                    low=df_processed['Low'], close=df_processed['Close'], 
                    name="Price Pattern"
                )])
                
                # Highlight zones dynamically on chart canvas
                if not zones_df.empty:
                    for _, row in zones_df.tail(8).iterrows():
                        color = "rgba(46, 204, 113, 0.15)" if "Demand" in row['Type'] else "rgba(231, 76, 60, 0.15)"
                        fig.add_shape(
                            type="rect", 
                            x0=row['Time'], y0=row['Distal'], 
                            x1=df_processed.index[-1], y1=row['Proximal'], 
                            fillcolor=color, line=dict(width=0)
                        )
                    
                fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Dynamic Table Engine
                st.subheader("📋 Core Zone Database Logs")
                if not zones_df.empty:
                    st.dataframe(zones_df.sort_values(by="Time", ascending=False), use_container_width=True)
                else:
                    st.info(f"No custom structural patterns detected for {zone_filter} filter rules currently.")
            else:
                st.error("No trading structural history received from data stream. Please verify ticker notation.")
        except Exception as err:
            st.error(f"Execution Error inside Data Engine: {err}")
