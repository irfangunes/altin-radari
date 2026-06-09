import streamlit as st
import pandas as pd
import warnings
import plotly.graph_objects as go
from tvDatafeed import TvDatafeed, Interval
from streamlit_autorefresh import st_autorefresh

warnings.filterwarnings('ignore')

# UYGULAMA EKRAN AYARLARI (Geniş Ekran)
st.set_page_config(page_title="Pro Altın Radarı", page_icon="🎯", layout="wide")
st.title("🎯 Pro Altın Radarı (Otomatik)")

# SİSTEMİ 60 SANİYEDE BİR SESSİZCE YENİLE
st_autorefresh(interval=60 * 1000, key="otomatik_yenileme")

def veri_cek():
    tv = TvDatafeed()
    df_1W = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_weekly, n_bars=5)
    df_1D = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_daily, n_bars=5)
    df_4H = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_4_hour, n_bars=5)
    df_canli = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_1_minute, n_bars=120)
    
    return df_canli, df_1W, df_1D, df_4H

try:
    with st.spinner("Piyasalar Taranıyor..."):
        df_canli, df_1W, df_1D, df_4H = veri_cek()
        son_fiyat = float(df_canli['close'].iloc[-1])
        onceki_fiyat = float(df_canli['close'].iloc[-2])
        fiyat_farki = son_fiyat - onceki_fiyat
    
    st.metric(label="XAUUSD (Spot Altın)", value=f"{son_fiyat:.2f} USD", delta=f"{fiyat_farki:.2f} USD")
    st.markdown("---")

    st.markdown("### 📊 Kritik Seviyeler (Otomatik)")
    k1, k2, k3 = st.columns(3)
    k1.info(f"**4 SAATLİK (Kısa)**\n\n🔴 Direnç: {df_4H['high'].iloc[-2]:.2f}\n\n🟢 Destek: {df_4H['low'].iloc[-2]:.2f}")
    k2.warning(f"**1 GÜNLÜK (Orta)**\n\n🔴 Direnç: {df_1D['high'].iloc[-2]:.2f}\n\n🟢 Destek: {df_1D['low'].iloc[-2]:.2f}")
    k3.error(f"**1 HAFTALIK (Uzun)**\n\n🔴 Direnç: {df_1W['high'].iloc[-2]:.2f}\n\n🟢 Destek: {df_1W['low'].iloc[-2]:.2f}")
    st.markdown("---")

    fig = go.Figure(data=[go.Candlestick(
        x=df_canli.index,
        open=df_canli['open'],
        high=df_canli['high'],
        low=df_canli['low'],
        close=df_canli['close'],
        name='Canlı',
        increasing_line_color='#089981', 
        decreasing_line_color='#F23645'  
    )])
    
    fig.update_layout(
        template='plotly_dark',
        height=450,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_rangeslider_visible=False 
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Bağlantı hatası: {e}")
