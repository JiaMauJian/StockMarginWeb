from datetime import datetime
import streamlit as st
from FinMind.data import DataLoader

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

st.title("台灣融資維持率 📈")

# 看一下資料
st.dataframe(df_margin.head())

# 繪圖
st.line_chart(
    df_margin,
    x="date",
    y="margin_maintenance_ratio"
)
