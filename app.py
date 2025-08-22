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

st.set_page_config(page_title="大盤指數與指標分析", layout="wide")
st.title("📈 大盤指數與指標分析")

# ===== 圖表1: TAIEX vs 融資維持率 =====
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_taiex["date"], y=df_taiex["close"],
    name="TAIEX", line=dict(color="blue")
))
fig1.add_trace(go.Scatter(
    x=df_margin["date"], y=df_margin["TotalExchangeMarginMaintenance"],
    name="融資維持率", line=dict(color="red"), yaxis="y2"
))
fig1.update_layout(
    yaxis=dict(title="TAIEX"),
    yaxis2=dict(title="融資維持率", overlaying="y", side="right", range=[50, 200]),
    title="TAIEX vs 融資維持率",
    width=1500,
    height=600
)
st.plotly_chart(fig1, use_container_width=True)

# ===== 圖表2: TAIEX vs CNN恐懼與貪婪指數 =====
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_taiex["date"], y=df_taiex["close"],
    name="TAIEX", line=dict(color="blue")
))
fig2.add_trace(go.Scatter(
    x=df_cnn["date"], y=df_cnn["fear_greed"],
    name="Fear/Greed", line=dict(color="orange"), yaxis="y2"
))
fig2.update_layout(
    yaxis=dict(title="TAIEX"),
    yaxis2=dict(title="Fear/Greed", overlaying="y", side="right", range=[0, 100]),
    title="TAIEX vs Fear/Greed Index",
    width=1500,
    height=600
)
st.plotly_chart(fig2, use_container_width=True)