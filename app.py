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
                if df.iloc[k]['is_green'] == direction_green and df
