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
# ⚙️ MULTI-CHANNEL TELEGRAM CONFIGURATION
# -------------------------------------------------------------------
TELEGRAM_TOKEN = "8781917241:AAFfyCdiJRCx321U_kVp0pJAe1fhKYcS5BU"
CHANNEL_IDS = {
    "Indian Stocks (Nifty 100)": "-1004441153450",
    "US Stocks (Nasdaq 100)": "-1004457256685",
    "Forex (Majors, Minors & Crosses)": "-1004448848917",
    "Commodities": "-1004448848917",
    "Crypto": "-1004451326458"
}

def send_market_specific_alert(category, message):
    if TELEGRAM_TOKEN == "YAHAN_APNA_BOT_TOKEN_PASTE_KAREIN": 
        return
    target_id = CHANNEL_IDS.get(category, CHANNEL_IDS["Forex (Majors, Minors & Crosses)"])
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": target_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception:
        pass

# -------------------------------------------------------------------
# 🎯 COMPLETE MASTER DATABASE INJECTED (100+100+35+COMMODITIES)
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
            "CSCO", "TMUS", "ADBE", "NFLX", "AMD", "CMCSA", "TXN", "QCOM", "INTC", "AMGN",
            "HON", "INTU", "AMAT", "BKNG", "SBUX", "MDLZ", "ISRG", "GILD", "LRCX", "REGN",
            "VRTX", "MU", "ADP", "PANW", "MELI", "SNPS", "CDNS", "KLAC", "CSX", "MAR",
            "ORLY", "ASML", "CTAS", "NXPI", "WDAY", "MNST", "ROP", "LULU", "ADSK", "CPRT",
            "AEP", "KDP", "MCHP", "ODFL", "PAYX", "PCAR", "DXCM", "CHTR", "MRVL", "LNT",
            "AZN", "EXC", "IDXX", "MSI", "CTSH", "FTNT", "GFL", "TEAM", "BKR", "DDOG",
            "PDD", "CEG", "GEHC", "ROST", "FAST", "VRSK", "BILI", "ANSS", "SIRI", "ALGN",
            "EA", "ILMN", "WBD", "MDB", "FANG", "TTWO", "OKTA", "SPLK", "DASH", "ZS",
            "CRWD", "COGN", "MSTR", "HOOD", "ARM", "PLTR", "SMCI", "APP", "AXON"
        ],
        "Forex (Majors, Minors & Crosses)": [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
            "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X",
            "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
            "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
            "CADJPY=X", "CADCHF=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "CHFJPY=X",
            "USDSGD=X", "USDHKD=X", "USDMXN=X", "USDSEK=X", "USDTRY=X", "EURTRY=X", "GBPSEK=X"
        ],
        "Commodities": [
            "GC=F", "SI=F", "PL=F", "PA=F", "CL=F", "BZ=F", "NG=F", "HG=F", "RB=F", "HO=F", "ZC=F", "ZS=F", "ZW=F"
        ],
        "Crypto": [
            "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"
        ]
    }

assets_master = get_complete_asset_database()

# 🛠️ ALL 17 TIMEFRAMES MASTER CONFIGURATION FOR MANUAL SCANS
TIMEFRAMES_MASTER = {
    "5 Min": {"base_interval": "5m", "period": "5d"},
    "15 Min": {"base_interval": "15m", "period": "5d"},
    "30 Min": {"base_interval": "30m", "period": "5d"},
    "45 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "45min"},
    "75 Min": {"base_interval": "15m", "period": "5d", "resample_rule": "75min"},
    "125 Min": {"base_interval": "5m", "period": "5d", "resample_rule": "125min"},
    "1 Hour": {"base_interval": "1h", "period": "360d"},
    "2 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "2h"},
    "4 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "4h"},
    "5 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "5h"},
    "6 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "6h"},
    "8 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "8h"},
    "10 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "10h"},
    "12 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "12h"},
    "16 Hour": {"base_interval": "1h", "period": "360d", "resample_rule": "16h"},
    "Daily": {"base_interval": "1d", "period": "5y"},
    "Weekly": {"base_interval": "1wk", "period": "max"}
}

# Advanced Resampling Engine
def apply_resampling(df, tf_name):
    if df.empty: 
        return df
    df = df.copy()
    if df.index.tz is not None: 
        df.index = df.index.tz_localize(None)
    
    config = TIMEFRAMES_MASTER[tf_name]
    if "resample_rule" in config:
        rule = config["resample_rule"]
        return df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    return df

# S&D Logic Engine
def scan_supply_demand_zones(
    df,
    symbol_name,
    tf_name,
    selected_base_counts,
    selected_legout_counts
):
    zones = []
    if len(df) < 12: 
        return zones
    df = df.copy()
    df['candle_size'] = (df['High'] - df['Low']).abs()
    df['body_size'] = (df['Close'] - df['Open']).abs()
    df['is_green'] = df['Close'] > df['Open']
    df['body_ratio'] = (df['body_size'] / df['candle_size'].replace(0, 0.0001)) * 100

        for i in range(5, len(df) - 3):
        for num_base in selected_base_counts:
            legin_idx = i - 1
            base_indices = list(range(i, i + num_base))
            legout_idx = i + num_base

            if legout_idx >= len(df):
                continue

            legin, legout = df.iloc[legin_idx], df.iloc[legout_idx]
            bases = df.iloc[base_indices]

            if legin['body_ratio'] < 70 or legout['body_ratio'] < 70:
                continue

            if legout['body_size'] <= legin['body_size']:
                continue

            legout_count = 1
            direction_green = legout['is_green']

            for k in range(legout_idx + 1, len(df)):
                if (
                    df.iloc[k]['is_green'] == direction_green
                    and df.iloc[k]['body_ratio'] >= 50
                ):
                    legout_count += 1
                else:
                    break

            legout_valid = False

            for req_legout in selected_legout_counts:

                if req_legout == "More Than 3":
                    if legout_count > 3:
                        legout_valid = True

                elif legout_count >= int(req_legout):
                    legout_valid = True

            if not legout_valid:
                continue

            legin_green = legin['is_green']
            legout_green = legout['is_green']

            pattern = None
z_type = None
proximal = 0.0
distal = 0.0
                    
            legin_green, legout_green = legin['is_green'], legout['is_green']
            pattern, z_type, proximal, distal = None, None, 0.0, 0.0
            
            if legin_green and legout_green: 
                pattern, z_type = "RBR", "Demand"
            elif legin_green and not legout_green: 
                pattern, z_type = "RBD", "Supply"
            elif not legin_green and legout_green: 
                pattern, z_type = "DBR", "Demand"
            elif not legin_green and not legout_green: 
                pattern, z_type = "DBD", "Supply"
                
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
                    if cl <= proximal: 
                        entered_zone = True
                    if entered_zone:
                        if cl < distal: 
                            status = "SL HIT"; break
                        elif ch >= target_price: 
                            status = "TARGET"; break
                else:
                    if ch >= proximal: 
                        entered_zone = True
                    if entered_zone:
                        if ch > distal: 
                            status = "SL HIT"; break
                        elif cl <= target_price: 
                            status = "TARGET"; break
                            
            zones.append({
                "Symbol": symbol_name, "Timeframe": tf_name, "Pattern": pattern, "Type": z_type,
                "Proximal": round(proximal, 4), "Distal": round(distal, 4), "Target (1:2)": round(target_price, 4),
                "Status": status, "Base Count": num_base, "Legout Count": legout_count,
                "Formed At": df.index[i].strftime('%Y-%m-%d %H:%M')
            })
    return zones

# -------------------------------------------------------------------
# CONTROL PANEL INTERFACE
# -------------------------------------------------------------------
st.markdown("### 🎛️ Scanner Control Matrix")
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    market_cat = st.selectbox("1. Choose Market Category", list(assets_master.keys()))
with row1_col2:
    symbols_options = ["🎨 [ALL SYMBOLS]"] + assets_master[market_cat]
    selected_symbol_raw = st.selectbox("2. Select Target Ticker / Pair List", symbols_options)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    selected_tf_labels = st.multiselect("3. Select Timeframes", list(TIMEFRAMES_MASTER.keys()), default=["1 Hour"])
with row2_col2:
    zone_filter_mode = st.radio("4. Target Zone Integrity Condition", ["FRESH", "SL HIT", "TARGET", "ALL"], horizontal=True)
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    selected_base_counts = st.multiselect(
        "5. Base Candle Count",
        [1, 2, 3],
        default=[1, 2, 3]
    )

with row3_col2:
    selected_legout_counts = st.multiselect(
        "6. Legout Count",
        [1, 2, 3, "More Than 3"],
        default=[1, 2, 3, "More Than 3"]
    )

if not selected_base_counts:
    selected_base_counts = [1, 2, 3]

if not selected_legout_counts:
    selected_legout_counts = [1, 2, 3, "More Than 3"]
send_alerts = st.checkbox("📢 Send Fresh Manual Scan Zones to Segregated Telegram Channels", value=True)
run_scan_btn = st.button("🚀 START STRUCTURAL MATRIX SCAN", use_container_width=True)
st.markdown("---")

# -------------------------------------------------------------------
# PIPELINE EXECUTION
# -------------------------------------------------------------------
if run_scan_btn:
    if selected_symbol_raw == "🎨 [ALL SYMBOLS]": 
        target_symbols = assets_master[market_cat]
    else: 
        target_symbols = [selected_symbol_raw]
        
    all_detected_zones = []
    
    with st.spinner(f"Scanning {len(target_symbols)} assets across custom resampled matrices..."):
        for symbol in target_symbols:
            for tf_label in selected_tf_labels:
                config = TIMEFRAMES_MASTER[tf_label]
                try:
                    raw_feed = yf.Ticker(symbol).history(period=config["period"], interval=config["base_interval"])
                    if raw_feed.empty: 
                        continue
                    processed_feed = apply_resampling(raw_feed, tf_label)
                    all_detected_zones.extend(
    scan_supply_demand_zones(
        processed_feed,
        symbol,
        tf_label,
        selected_base_counts,
        selected_legout_counts
    )
)
                except Exception:
                    continue

    if all_detected_zones:
        master_df = pd.DataFrame(all_detected_zones)
        
        total_fresh = len(master_df[master_df["Status"] == "FRESH"])
        total_target = len(master_df[master_df["Status"] == "TARGET"])
        total_sl_hit = len(master_df[master_df["Status"] == "SL HIT"])
        
        if zone_filter_mode != "ALL":
            master_df = master_df[master_df["Status"] == zone_filter_mode]
            
        st.success(f"📊 Matrix Sweep Completed! Displaying {len(master_df)} rows based on filter.")
        
        # Segmented Telegram Dispatch
        if send_alerts and not master_df.empty:
            for _, alert_row in master_df.iterrows():
                if alert_row['Status'] == "FRESH":
                    main_emoji = "🟢" if alert_row['Type'] == "Demand" else "🔴"
                    display_status = "FRESH"
                elif alert_row['Status'] == "SL HIT":
                    main_emoji = "❌"
                    display_status = "VIOLATED (SL HIT)"
                else:
                    main_emoji = "🎉"
                    display_status = "VIOLATED (TARGET HIT)"
                    
                alert_msg = (
                    f"{main_emoji} *MANUAL SCANNER UPDATE* {main_emoji}\n\n"
                    f"▪️ *SYMBOL :* `{alert_row['Symbol']}`\n"
                    f"▪️ *TIMEFRAME :* `{alert_row['Timeframe']}`\n"
                    f"▪️ *PATTERN :* `{alert_row['Pattern']}`\n"
                    f"▪️ *TYPE :* `{alert_row['Type'].upper()}`\n"
                    f"▪️ *BASE COUNT :* `{alert_row['Base Count']}`\n"
                    f"▪️ *LEGOUTILITY COUNT :* `{alert_row['Legout Count']}`\n"
                    f"▪️ *STATUS :* `{display_status}`\n"
                    f"▪️ *PROXIMAL LINE :* `{alert_row['Proximal']}`\n"
                    f"▪️ *DISTAL LINE :* `{alert_row['Distal']}`\n"
                    f"▪️ *TARGET (1:2) :* `{alert_row['Target (1:2)']}`\n"
                    f"▪️ *DATE OF ZONE FORMED :* `{alert_row['Formed At']}`"
                )
                send_market_specific_alert(market_cat, alert_msg)
            
            st.info("📢 Scan results and zones have been processed/sent to Telegram.")

        # Metrics Panel
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scanned Assets", f"{len(target_symbols)} Pairs")
        m2.metric("🟢 Fresh Active Zones", total_fresh)
        m3.metric("🎯 Target Hits (1:2 RR)", total_target)
        m4.metric("🔴 Stop Loss (SL) Hits", total_sl_hit)
        
        clean_columns = ["Symbol", "Timeframe", "Pattern", "Type", "Base Count", "Legout Count", "Status", "Proximal", "Distal", "Target (1:2)", "Formed At"]
        master_df = master_df[clean_columns]
        
        st.subheader("📋 Core Structural Database Logs")
        st.dataframe(master_df.sort_values(by="Formed At", ascending=False), use_container_width=True)
        
        # Charts Matrix
        st.markdown("### 🔍 Live Visual Chart Matrix")
        for idx, row in master_df.sort_values(by="Formed At", ascending=False).head(10).iterrows():
            with st.expander(f"📈 {row['Symbol']} | {row['Timeframe']} | {row['Status']}"):
                config = TIMEFRAMES_MASTER[row['Timeframe']]
                try:
                    chart_feed = apply_resampling(yf.Ticker(row['Symbol']).history(period=config["period"], interval=config["base_interval"]), row['Timeframe'])
                    if not chart_feed.empty:
                        fig = go.Figure(data=[go.Candlestick(x=chart_feed.index, open=chart_feed['Open'], high=chart_feed['High'], low=chart_feed['Low'], close=chart_feed['Close'], name="Price")])
                        sc = "rgba(46, 204, 113, 0.15)" if row['Type'] == "Demand" else "rgba(231, 76, 60, 0.15)"
                        lc = "#2ecc71" if row['Type'] == "Demand" else "#e74c3c"
                        fig.add_shape(type="rect", x0=row['Formed At'], y0=row['Distal'], x1=chart_feed.index[-1], y1=row['Proximal'], fillcolor=sc, line=dict(color=lc, width=1))
                        fig.add_shape(type="line", x0=row['Formed At'], y0=row['Target (1:2)'], x1=chart_feed.index[-1], y1=row['Target (1:2)'], line=dict(color="#3498db", width=2, dash="dash"))
                        fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True, key=f"ch_{idx}")
                except Exception: 
                    st.error("Chart render error.")
    else:
        st.info("No structural zones detected for this selection.")
