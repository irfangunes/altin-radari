import streamlit as st
import pandas as pd
import warnings
import plotly.graph_objects as go
from tvDatafeed import TvDatafeed, Interval
from streamlit_autorefresh import st_autorefresh

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Pro Altın Radarı", page_icon="🎯", layout="wide")
st.title("🎯 Pro Altın Radarı (İndikatörlü)")

st_autorefresh(interval=60 * 1000, key="otomatik_yenileme")

def veri_cek():
    tv = TvDatafeed()
    df_canli = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_1_minute, n_bars=120)
    # Destek/Direnç için günlük veri
    df_gunluk = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=Interval.in_daily, n_bars=20)
    
    # İNDİKATÖR HESAPLAMALARI
    df = df_canli.copy()
    df['Close'] = df['close'].astype(float)
    
    # Bollinger Bantları
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['std'] = df['Close'].rolling(window=20).std()
    df['Bol_Ust'] = df['SMA_20'] + (df['std'] * 2)
    df['Bol_Alt'] = df['SMA_20'] - (df['std'] * 2)
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df, df_gunluk['high'].max(), df_gunluk['low'].min()

try:
    with st.spinner("İndikatörler hesaplanıyor..."):
        df, direnc, destek = veri_cek()
        son = df.iloc[-1]
    
    # Özet Panosu
    c1, c2, c3 = st.columns(3)
    c1.metric("Fiyat", f"{son['Close']:.2f}")
    c2.metric("RSI", f"{son['RSI']:.1f}")
    c3.metric("Trend", "Pozitif" if son['Close'] > son['SMA_20'] else "Negatif")

    # Grafik
    fig = go.Figure()
    # Mumlar
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['Close'], name='Fiyat'))
    # Bollinger
    fig.add_trace(go.Scatter(x=df.index, y=df['Bol_Ust'], line=dict(color='gray', width=1), name='Bollinger Üst'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Bol_Alt'], line=dict(color='gray', width=1), name='Bollinger Alt'))
    # Destek/Direnç
    fig.add_hline(y=direnc, line_dash="dash", line_color="red", annotation_text="Direnç")
    fig.add_hline(y=destek, line_dash="dash", line_color="green", annotation_text="Destek")

    fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Hata: {e}")
