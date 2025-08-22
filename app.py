from datetime import datetime
import pandas as pd
import requests
import streamlit as st
from FinMind.data import DataLoader
import plotly.graph_objects as go

# 讀取 FinMind token
token = st.secrets["FinMind"]["token"]
api = DataLoader()
api.login_by_token(api_token=token)

START_DATE = "2000-01-01"
TODAY = datetime.today().strftime("%Y-%m-%d")

# 取得融資維持率
df_margin = api.taiwan_total_exchange_margin_maintenance(
    start_date=START_DATE,
    end_date=TODAY
)
df_margin["source"] = "margin_maintenance"

# 上市指數 TAIEX
df_taiex = api.taiwan_stock_daily(
    stock_id="TAIEX", start_date=START_DATE, end_date=TODAY
)
df_taiex["source"] = "TAIEX"

# CNN Fear/Greed
url = "https://api.finmindtrade.com/api/v4/data"
form_data = {
    "dataset": "CnnFearGreedIndex",
    "start_date": START_DATE,
    "end_date": TODAY,
}
headers = {"Authorization": f"Bearer {token}"}
res = requests.get(url, params=form_data, headers=headers)
temp = res.json()
df_cnn = pd.DataFrame(temp["data"])
df_cnn["source"] = "CNN_FearGreed"

col1, col2, col3 = st.columns([1, 4, 1])  # 中間寬一點，左右留白
with col2:
    st.set_page_config(page_title="大盤指數與指標分析", layout="wide")
    st.title("📈 大盤指數與指標分析")

    # 設定年份範圍 (2000 ~ 今年)
    current_year = datetime.today().year
    year_range = st.slider(
        "選擇年份區間：",
        min_value=2000,
        max_value=current_year,
        value=(current_year - 5, current_year),  # 預設區間：當前年份往前推5年
        step=1
    )

    st.write(f"你選擇的年份區間是 {year_range[0]} ~ {year_range[1]}")

    # 取得年份區間
    year_start, year_end = year_range

    # 過濾 TAIEX
    df_taiex["year"] = pd.to_datetime(df_taiex["date"]).dt.year
    df_taiex_filtered = df_taiex[(df_taiex["year"] >= year_start) & (df_taiex["year"] <= year_end)]

    # 過濾融資維持率
    df_margin["year"] = pd.to_datetime(df_margin["date"]).dt.year
    df_margin_filtered = df_margin[(df_margin["year"] >= year_start) & (df_margin["year"] <= year_end)]

    # 過濾 Fear/Greed
    df_cnn["year"] = pd.to_datetime(df_cnn["date"]).dt.year
    df_cnn_filtered = df_cnn[(df_cnn["year"] >= year_start) & (df_cnn["year"] <= year_end)]

    # ===== 圖表1: TAIEX vs 融資維持率 =====
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_taiex_filtered["date"], y=df_taiex_filtered["close"],
        name="TAIEX", line=dict(color="blue")
    ))
    fig1.add_trace(go.Scatter(
        x=df_margin_filtered["date"], y=df_margin_filtered["TotalExchangeMarginMaintenance"],
        name="融資維持率", line=dict(color="red"), yaxis="y2"
    ))
    fig1.update_layout(
        yaxis=dict(title="TAIEX"),
        yaxis2=dict(title="融資維持率", overlaying="y", side="right", range=[50, 200]),
        title=f"TAIEX vs 融資維持率 ({year_start}~{year_end})",
        width=1200,
        height=600
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ===== 圖表2: TAIEX vs CNN恐懼與貪婪指數 =====
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_taiex_filtered["date"], y=df_taiex_filtered["close"],
        name="TAIEX", line=dict(color="blue")
    ))
    fig2.add_trace(go.Scatter(
        x=df_cnn_filtered["date"], y=df_cnn_filtered["fear_greed"],
        name="Fear/Greed", line=dict(color="orange"), yaxis="y2"
    ))
    fig2.update_layout(
        yaxis=dict(title="TAIEX"),
        yaxis2=dict(title="Fear/Greed", overlaying="y", side="right", range=[0, 100]),
        title=f"TAIEX vs Fear/Greed Index ({year_start}~{year_end})",
        width=1200,
        height=600
    )
    st.plotly_chart(fig2, use_container_width=True)

