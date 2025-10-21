
# app.py
# ================================================================
# 🌍 Global Macro Dashboard — Tudo-em-Um
# Streamlit + Plotly Express + tvDatafeed + pandas_datareader (FRED)
# ================================================================
import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from datetime import date, timedelta

#python -m streamlit run C:\Users\andre\streamlit_dash.py --server.address localhost --server.port 8520


# Data sources
from pandas_datareader import data as pdr
try:
    from tvDatafeed import TvDatafeed, Interval
    TV_AVAILABLE = True
except Exception:
    TV_AVAILABLE = False

st.set_page_config(page_title="Global Macro Dashboard", layout="wide")

st.title("🌍 Global Macro Dashboard — Juros, CDS, Bolsas, Commodities, TIPS")
st.caption("Fonte: TradingView (tvDatafeed), FRED (pandas_datareader) e TradingEconomics (via TradingView).")

# -------------------------------
# Sidebar — credenciais e opções globais
# -------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")
    st.write("Para séries do TradingView, informe login (recomendado). Para FRED, não precisa chave.")
    tv_user = st.text_input("TradingView usuário", value="andre_trierveiler", type="default")
    tv_pass = st.text_input("TradingView senha", value="Senha8aa*8", type="password")
    st.divider()
    min_date = date(2003, 1, 1)
    default_start = date.today() - timedelta(days=365*5)
    d_start = st.date_input("Início (global)", value=default_start, min_value=min_date, max_value=date.today())
    d_end = st.date_input("Fim (global)", value=date.today(), min_value=min_date, max_value=date.today())
    st.divider()
    normalize = st.checkbox("Normalizar (base 100)", value=False)
    returns_mode = st.selectbox("Séries transformadas", ["Nível", "Retorno diário (%)", "Retorno acumulado (%)"], index=0)

# Helper: connect to TradingView
@st.cache_resource(show_spinner=False)
def get_tv(user, pwd):
    if not TV_AVAILABLE:
        return None
    try:
        if user and pwd:
            tv = TvDatafeed(username=user, password=pwd)
        else:
            # guest mode (histórico reduzido)
            tv = TvDatafeed()
        return tv
    except Exception as e:
        st.warning(f"Não foi possível iniciar tvDatafeed: {e}")
        return None

tv = get_tv(tv_user, tv_pass)

# Helper: transform series according to sidebar
def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_index()
    if returns_mode == "Nível":
        out = df.copy()
    elif returns_mode == "Retorno diário (%)":
        out = df.pct_change()*100
    else:
        out = (1+df.pct_change()).cumprod()*100 - 100
    if normalize and returns_mode == "Nível":
        out = (out / out.iloc[0])*100
    return out

# -------------------------------
# Fetchers
# -------------------------------
def fetch_fred(series_code: str, start_date, end_date) -> pd.DataFrame:
    try:
        s = pdr.DataReader(series_code, "fred", start_date, end_date)
        s = s.rename(columns={series_code: "value"})
        return s
    except Exception as e:
        st.warning(f"FRED falhou para {series_code}: {e}")
        return pd.DataFrame(columns=["value"])

def fetch_tv(symbol: str, exchange: str, interval= "D", n_bars=1000) -> pd.DataFrame:
    if tv is None:
        return pd.DataFrame(columns=["close"])
    try:
        # map interval
        if interval == "D":
            iv = Interval.in_daily
        elif interval == "W":
            iv = Interval.in_weekly
        elif interval == "M":
            iv = Interval.in_monthly
        else:
            iv = Interval.in_daily
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=iv, n_bars=n_bars)
        return df
    except Exception as e:
        st.warning(f"TradingView falhou para {exchange}:{symbol} — {e}")
        return pd.DataFrame(columns=["close"])

# ================================================================
# Tabs
# ================================================================
tab_rates, tab_cds, tab_equities, tab_cmd, tab_tips, tab_corr = st.tabs([
    "📉 Juros Globais",
    "🛡️ CDS 5Y",
    "📊 Índices & ESG",
    "🛢️ Commodities",
    "🇺🇸 TIPS & Breakeven",
    "🔗 Correlações"
])

# ================================================================
# 📉 Juros Globais (2y/5y/10y proxies e futuros)
# ================================================================
with tab_rates:
    st.subheader("📉 Juros/Curvas — 2y / 5y / 10y")
    st.markdown("Combinação de **futuros** (B3, CME/CBOT, EUREX) e **yields soberanos** (TradingEconomics via TradingView).")

    # 10Y yields (TradingEconomics proxies) & futures main
    tickers_rates = {
        # Brasil — DI1 (preço → 100 - preço = taxa implícita)
        "BRAZIL_DI1_2025 (preço)": ("DI1F2025", "BMFBOVESPA", "price"),
        "BRAZIL_DI1_2029 (preço)": ("DI1F2029", "BMFBOVESPA", "price"),
        # EUA
        "US_FedFunds_Dec25 (preço)": ("ZQZ2025", "CBOT", "price"),
        "US_10Y_Fut (preço)": ("ZN1!", "CBOT", "price"),
        "US_10Y_Yield (%)": ("US10Y", "TRADINGECONOMICS", "yield"),
        # Reino Unido
        "UK_10Y_Yield (%)": ("UK10Y", "TRADINGECONOMICS", "yield"),
        # Alemanha
        "GER_Bund_10Y_Fut (preço)": ("FGBL1!", "EUREX", "price"),
        "GER_10Y_Yield (%)": ("DE10Y", "TRADINGECONOMICS", "yield"),
        # Japão
        "JAPAN_10Y_Fut (preço)": ("JGB1!", "TSE", "price"),
        "JAPAN_10Y_Yield (%)": ("JP10Y", "TRADINGECONOMICS", "yield"),
        # China
        "CHINA_10Y_Yield (%)": ("CN10Y", "TRADINGECONOMICS", "yield"),
        # Turquia / Chile / Argentina / México
        "TURKEY_10Y_Yield (%)": ("TURKEY10Y", "TRADINGECONOMICS", "yield"),
        "CHILE_10Y_Yield (%)": ("CHILE10Y", "TRADINGECONOMICS", "yield"),
        "ARGENTINA_10Y_Yield (%)": ("ARGENTINA10Y", "TRADINGECONOMICS", "yield"),
        "MEXICO_10Y_Yield (%)": ("MEXICO10Y", "TRADINGECONOMICS", "yield"),
        # 5Y proxies
        "USA_5Y_Fut (preço)": ("ZF1!", "CBOT", "price"),
        "GERMANY_5Y_Fut (preço)": ("FGBM1!", "EUREX", "price"),
        "UK_5Y_Yield (%)": ("UK5Y", "TRADINGECONOMICS", "yield"),
        "JAPAN_5Y_Yield (%)": ("JP5Y", "TRADINGECONOMICS", "yield"),
        "CHINA_5Y_Yield (%)": ("CN5Y", "TRADINGECONOMICS", "yield"),
        "TURKEY_5Y_Yield (%)": ("TURKEY5Y", "TRADINGECONOMICS", "yield"),
        "CHILE_5Y_Yield (%)": ("CHILE5Y", "TRADINGECONOMICS", "yield"),
        "ARGENTINA_5Y_Yield (%)": ("ARGENTINA5Y", "TRADINGECONOMICS", "yield"),
        "MEXICO_5Y_Yield (%)": ("MEXICO5Y", "TRADINGECONOMICS", "yield"),
        # Brasil ~5Y via DI2030
        "BRAZIL_DI1_2030 (preço)": ("DI1F2030", "BMFBOVESPA", "price")
    }

    data_rates = {}
    for name, (sym, exch, kind) in tickers_rates.items():
        df = fetch_tv(sym, exch, "D", 1500)
        if df is not None and not df.empty:
            series = df["close"].copy()
            if kind == "price":
                # converter preço de futuro de juros em taxa implícita (aproximação) → 100 - preço
                series = 100 - series
            data_rates[name] = series

    if data_rates:
        df_rates = pd.concat(data_rates, axis=1)
        # filtra data range
        df_rates = df_rates[(df_rates.index.date >= d_start) & (df_rates.index.date <= d_end)]
        plot_df = transform_df(df_rates)
        st.plotly_chart(px.line(plot_df, labels={"value":"%", "index":"Data"}), use_container_width=True)
        st.dataframe(plot_df.tail(), use_container_width=True)
        st.download_button("📥 Baixar CSV (juros)",
                           data=plot_df.to_csv().encode("utf-8"),
                           file_name="global_rates.csv", mime="text/csv")
    else:
        st.warning("Nenhuma série de juros carregada (verifique login do TradingView).")

# ================================================================
# 🛡️ CDS 5Y (FRED — IHS Markit)
# ================================================================
with tab_cds:
    st.subheader("🛡️ CDS Soberano — 5 anos (bps)")
    cds_map = {
        "BRAZIL": "BRACDS05",
        "USA": "USACDS05",
        "UK": "GBRCDS05",
        "GERMANY": "DEUCDS05",
        "JAPAN": "JPACDS05",
        "CHINA": "CHNCDS05",
        "CHILE": "CHLCDS05",
        "TURKEY": "TURCDS05",
        "ARGENTINA": "ARGCDS05",
        "MEXICO": "MEXCDS05"
    }
    frames = []
    for k, code in cds_map.items():
        s = fetch_fred(code, d_start, d_end)
        if not s.empty:
            s = s.rename(columns={"value": k})
            frames.append(s[k])
    if frames:
        df_cds = pd.concat(frames, axis=1)
        st.plotly_chart(px.line(df_cds, labels={"value":"bps", "index":"Data"}), use_container_width=True)
        st.dataframe(df_cds.tail(), use_container_width=True)
        st.download_button("📥 Baixar CSV (CDS 5Y)", data=df_cds.to_csv().encode("utf-8"),
                           file_name="cds_5y.csv", mime="text/csv")
    else:
        st.warning("Nenhuma série CDS carregada (verifique conexão FRED).")

# ================================================================
# 📊 Índices & ESG
# ================================================================
with tab_equities:
    st.subheader("📊 Índices de Bolsa — Spot & ESG")
    tickers_eq = {
        # EUA spot
        "SP500_SPX": ("SPX", "SP"),
        "NASDAQ100_NDX": ("NDX", "NASDAQ"),
        # Brasil e México
        "IBOV": ("IBOV", "BMFBOVESPA"),
        "MEXICO_IPC": ("IPC", "BMV"),
        # Europa e Ásia
        "EUROSTOXX50": ("STOXX50E", "INDEX"),
        "DAX": ("DAX", "XETR"),
        "FTSE100": ("UKX", "INDEX"),
        "JAPAN_NIKKEI225": ("NKY", "INDEX"),
        "INDIA_NIFTY50": ("NIFTY", "NSE"),
        "HANG_SENG": ("HSI", "HSI"),
        "CHINA_CSI300": ("CSI300", "SSE"),
        # ESG / MSCI (proxies via ETFs/índices)
        "ISE_BRAZIL_ESG": ("ISE", "BMFBOVESPA"),
        "SP500_ESG": ("SPXESG", "SP"),
        "MSCI_WORLD_ESG": ("SUSW", "SWISS"),
        "MSCI_EM_ESG": ("SUSEME", "SWISS"),
        "MSCI_EM (EEM ETF)": ("EEM", "AMEX"),
        "MSCI_WORLD (URTH ETF)": ("URTH", "AMEX"),
        "MSCI_BRAZIL (EWZ ETF)": ("EWZ", "AMEX")
    }
    data_eq = {}
    for name, (sym, exch) in tickers_eq.items():
        df = fetch_tv(sym, exch, "D", 2000)
        if df is not None and not df.empty:
            data_eq[name] = df["close"]
    if data_eq:
        df_eq = pd.concat(data_eq, axis=1)
        df_eq = df_eq[(df_eq.index.date >= d_start) & (df_eq.index.date <= d_end)]
        plot_df = transform_df(df_eq)
        st.plotly_chart(px.line(plot_df, labels={"value":"nível/retorno", "index":"Data"}), use_container_width=True)
        st.dataframe(plot_df.tail(), use_container_width=True)
        st.download_button("📥 Baixar CSV (índices)",
                           data=plot_df.to_csv().encode("utf-8"),
                           file_name="equities.csv", mime="text/csv")
    else:
        st.warning("Nenhum índice carregado (TradingView).")

# ================================================================
# 🛢️ Commodities
# ================================================================
with tab_cmd:
    st.subheader("🛢️ Commodities (spot)")
    tickers_cmd = {
        "GOLD_SPOT (XAUUSD)": ("XAUUSD", "OANDA"),
        "SILVER_SPOT (XAGUSD)": ("XAGUSD", "OANDA"),
        "WTI_CRUDE (USOIL)": ("USOIL", "TVC"),
        "COPPER_SPOT": ("COPPER", "TVC")
    }
    data_cmd = {}
    for name, (sym, exch) in tickers_cmd.items():
        df = fetch_tv(sym, exch, "D", 2000)
        if df is not None and not df.empty:
            data_cmd[name] = df["close"]
    if data_cmd:
        df_cmd = pd.concat(data_cmd, axis=1)
        df_cmd = df_cmd[(df_cmd.index.date >= d_start) & (df_cmd.index.date <= d_end)]
        plot_df = transform_df(df_cmd)
        st.plotly_chart(px.line(plot_df, labels={"value":"USD", "index":"Data"}), use_container_width=True)
        st.dataframe(plot_df.tail(), use_container_width=True)
        st.download_button("📥 Baixar CSV (commodities)",
                           data=plot_df.to_csv().encode("utf-8"),
                           file_name="commodities.csv", mime="text/csv")
    else:
        st.warning("Nenhuma commodity carregada (TradingView).")

# ================================================================
# 🇺🇸 TIPS & Breakeven (FRED)
# ================================================================
with tab_tips:
    st.subheader("🇺🇸 TIPS (reais), Nominais e Breakeven — FRED")
    TENOR_TO_SERIES = {
        "2Y": {"real": "DFII2", "nominal": "DGS2"},
        "5Y": {"real": "DFII5", "nominal": "DGS5"},
        "10Y": {"real": "DFII10", "nominal": "DGS10"},
        "30Y": {"real": "DFII30", "nominal": "DGS30"}
    }
    tenors = st.multiselect("Prazos", ["2Y","5Y","10Y","30Y"], default=["2Y","5Y","10Y","30Y"])
    frames = []
    for t in tenors:
        codes = TENOR_TO_SERIES[t]
        dr = fetch_fred(codes["real"], d_start, d_end)
        dn = fetch_fred(codes["nominal"], d_start, d_end)
        if not dr.empty:
            dr = dr.rename(columns={"value": f"TIPS_{t}"})
            frames.append(dr[f"TIPS_{t}"])
        if not dn.empty:
            dn = dn.rename(columns={"value": f"Treasury_{t}"})
            frames.append(dn[f"Treasury_{t}"])
        if not dr.empty and not dn.empty:
            be = pd.DataFrame(index=dr.index).join(dn).join(dr)
            be[f"Breakeven_{t}"] = be[f"Treasury_{t}"] - be[f"TIPS_{t}"]
            frames.append(be[f"Breakeven_{t}"])
    if frames:
        df_tips = pd.concat(frames, axis=1)
        st.plotly_chart(px.line(df_tips, labels={"value":"% a.a.", "index":"Data"}), use_container_width=True)
        st.dataframe(df_tips.tail(), use_container_width=True)
        st.download_button("📥 Baixar CSV (TIPS & Breakeven)",
                           data=df_tips.to_csv().encode("utf-8"),
                           file_name="tips_breakeven.csv", mime="text/csv")
    else:
        st.warning("Nenhuma série TIPS/Nominal carregada (FRED).")

# ================================================================
# 🔗 Correlações
# ================================================================
with tab_corr:
    st.subheader("🔗 Correlações (selecionador de tabela base)")
    source = st.selectbox("Escolha a base de dados", ["Juros", "CDS", "Índices", "Commodities", "TIPS & Breakeven"])
    data_map = {}
    # Recompute minimal datasets aligned with global date range
    if source == "Juros":
        st.info("Use a aba Juros primeiro para garantir carregamento (depende do TradingView).")
    elif source == "CDS":
        # same as tab_cds quickly
        cds_map = {"BRAZIL":"BRACDS05","USA":"USACDS05","UK":"GBRCDS05","GERMANY":"DEUCDS05",
                   "JAPAN":"JPACDS05","CHINA":"CHNCDS05","CHILE":"CHLCDS05","TURKEY":"TURCDS05",
                   "ARGENTINA":"ARGCDS05","MEXICO":"MEXCDS05"}
        frames = []
        for k, code in cds_map.items():
            s = fetch_fred(code, d_start, d_end)
            if not s.empty:
                frames.append(s.rename(columns={"value": k})[k])
        if frames:
            base = pd.concat(frames, axis=1)
        else:
            base = pd.DataFrame()
    elif source == "Índices":
        eqt = {
            "SPX": ("SPX","SP"), "NDX": ("NDX","NASDAQ"), "IBOV": ("IBOV","BMFBOVESPA"),
            "EUROSTOXX50": ("STOXX50E","INDEX"), "DAX": ("DAX","XETR"), "NIKKEI225": ("NKY","INDEX"),
            "NIFTY50": ("NIFTY","NSE"), "HSI": ("HSI","HSI"), "CSI300": ("CSI300","SSE"),
            "EEM": ("EEM","AMEX"), "URTH": ("URTH","AMEX"), "EWZ": ("EWZ","AMEX")
        }
        frames = []
        for k,(s,e) in eqt.items():
            df = fetch_tv(s,e,"D",1500)
            if not df.empty:
                frames.append(df["close"].rename(k))
        base = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    elif source == "Commodities":
        cmd = {"XAUUSD":("XAUUSD","OANDA"), "XAGUSD":("XAGUSD","OANDA"), "USOIL":("USOIL","TVC"), "COPPER":("COPPER","TVC")}
        frames = []
        for k,(s,e) in cmd.items():
            df = fetch_tv(s,e,"D",1500)
            if not df.empty:
                frames.append(df["close"].rename(k))
        base = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    else:  # TIPS & Breakeven
        tmap = {"2Y":("DFII2","DGS2"), "5Y":("DFII5","DGS5"), "10Y":("DFII10","DGS10"), "30Y":("DFII30","DGS30")}
        frames = []
        for tenor,(r,n) in tmap.items():
            dr = fetch_fred(r, d_start, d_end).rename(columns={"value":f"TIPS_{tenor}"})
            dn = fetch_fred(n, d_start, d_end).rename(columns={"value":f"Treasury_{tenor}"})
            if not dr.empty: frames.append(dr[f"TIPS_{tenor}"])
            if not dn.empty: frames.append(dn[f"Treasury_{tenor}"])
            if not dr.empty and not dn.empty:
                be = dn.join(dr, how="inner")
                frames.append((be[f"Treasury_{tenor}"]-be[f"TIPS_{tenor}"]).rename(f"Breakeven_{tenor}"))
        base = pd.concat(frames, axis=1) if frames else pd.DataFrame()

    if base is None or base.empty:
        st.warning("Base vazia — carregue dados nas abas e/ou verifique conexões.")
    else:
        base = base[(base.index.date >= d_start) & (base.index.date <= d_end)]
        base_ret = base.pct_change().dropna(how="all")
        corr = base_ret.corr()
        st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r",
                                  zmin=-1, zmax=1, title="Correlação de retornos (diários)"),
                        use_container_width=True)
        st.dataframe(corr, use_container_width=True)
        st.download_button("📥 Baixar CSV (correlação)",
                           data=corr.to_csv().encode("utf-8"),
                           file_name="correlacao.csv", mime="text/csv")
