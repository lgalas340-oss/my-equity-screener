import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import io
import concurrent.futures

# --- CONFIGURATION ---
st.set_page_config(page_title="EQUITY INTELLIGENCE EUROPE", layout="wide", page_icon="🇪🇺")

st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #003366; font-weight: 700; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #003366; color: white; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES EUROPÉENNE COMPLÈTE ---
TICKERS_DATA = {
    "FRANCE (SBF 120 + LARGE SMALL CAPS)": list(set([
        "AC.PA", "AI.PA", "AIR.PA", "BNP.PA", "EN.PA", "CAP.PA", "CA.PA", "ACA.PA", "BN.PA", "DSY.PA", 
        "EL.PA", "ENGI.PA", "ERF.PA", "RMS.PA", "KER.PA", "OR.PA", "LR.PA", "MC.PA", "ML.PA", "ORAN.PA", 
        "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA", "SAN.PA", "SU.PA", "GLE.PA", "SW.PA", "STM.PA", 
        "TEP.PA", "HO.PA", "TTE.PA", "VIE.PA", "VIV.PA", "VLO.PA", "WLN.PA", "AKE.PA", "ALM.PA", "AMUN.PA", 
        "ATO.PA", "ATE.PA", "BOL.PA", "BVI.PA", "CO.PA", "COFA.PA", "DEC.PA", "DIM.PA", "EDEN.PA", "ELIS.PA", 
        "ESI.PA", "ETL.PA", "FDJ.PA", "FRVIA.PA", "GFT.PA", "GET.PA", "GFC.PA", "ICADE.PA", "IMB.PA", "INF.PA", 
        "IPS.PA", "KOF.PA", "LI.PA", "MDM.PA", "MF.PA", "NK.PA", "NXI.PA", "POM.PA", "RCO.PA", "RUI.PA", 
        "SCR.PA", "SESG.PA", "SOP.PA", "SPIE.PA", "SK.PA", "UBI.PA", "UPM.PA", "VALL.PA", "VIRI.PA", "ABCA.PA", 
        "ADP.PA", "ALD.PA", "ALTA.PA", "ALT.PA", "BAM.PA", "BEN.PA", "COV.PA", "DBV.PA", "EKT.PA", "EOS.PA", 
        "ERA.PA", "EUC.PA", "IDL.PA", "IORA.PA", "IPH.PA", "JCD.PA", "KORI.PA", "LSS.PA", "MERY.PA", "NRO.PA", 
        "OVH.PA", "RBT.PA", "SMCP.PA", "SOI.PA", "TFF.PA", "TNG.PA", "VALN.PA", "VIG.PA", "VIRP.PA", "VRAP.PA", 
        "ALVIV.PA", "WAGA.PA", "MCPHY.PA", "VANT.PA", "ES.PA", "GTT.PA", "SBT.PA", "ALFEN.PA", "ALBIO.PA", 
        "ALMGS.PA", "ALVDM.PA", "ARGAN.PA", "BIG.PA", "CAT.PA", "CGG.PA", "DBT.PA", "EKI.PA", "FII.PA", 
        "GUI.PA", "LNA.PA", "MAU.PA", "MEMS.PA", "NEX.PA", "NRJ.PA", "OMS.PA", "PAST.PA", "PLUX.PA", "RENE.PA", 
        "SCHP.PA", "SEB.PA", "SII.PA", "STIF.PA", "VGM.PA", "VOLUNT.PA", "XFAB.PA", "ALGAU.PA", "ALNEV.PA", 
        "ALSTR.PA", "BOIRON.PA", "ECA.PA", "KEY.PA", "LCO.PA", "MEDIC.PA", "PROX.PA", "STAS.PA"
    ])),
    "ALLEMAGNE (DAX & MDAX)": [
        "ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DB1.DE", 
        "DBK.DE", "EOAN.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "DHL.DE", "LIN.DE", "MBG.DE", 
        "MRK.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SHL.DE", 
        "SY1.DE", "VNA.DE", "VOW3.DE", "ZAL.DE", "AIXA.DE", "ARL.DE", "BOSS.DE", "EVK.DE", "FRA.DE", "HNR1.DE"
    ],
    "ESPAGNE (IBEX 35)": [
        "ANA.MC", "ACX.MC", "ACS.MC", "AENA.MC", "AMS.MC", "SAB.MC", "SAN.MC", "BKT.MC", "BBVA.MC", "CABK.MC", 
        "CLNX.MC", "ENG.MC", "ELE.MC", "FER.MC", "FLUI.MC", "GRF.MC", "IAG.MC", "IBE.MC", "ITX.MC", "IDR.MC", 
        "MAP.MC", "MEL.MC", "MRL.MC", "REP.MC", "TEF.MC"
    ],
    "ITALIE (FTSE MIB)": [
        "A2A.MI", "AMP.MI", "AZM.MI", "BAMI.MI", "BCA.MI", "BMED.MI", "BPE.MI", "ENI.MI", "ENEL.MI", "ERG.MI", 
        "G.MI", "ISP.MI", "LDO.MI", "MB.MI", "MONC.MI", "PRY.MI", "PST.MI", "REC.MI", "STLAM.MI", "TEN.MI", 
        "TRN.MI", "UCG.MI", "UNI.MI"
    ],
    "BENELUX (AEX / BEL 20)": [
        "AD.AS", "AKZA.AS", "ASML.AS", "ASM.AS", "BESI.AS", "HEIA.AS", "INGA.AS", "KPN.AS", "PRX.AS", "SHEL.AS", 
        "UNA.AS", "WKL.AS", "ABI.BR", "ACKB.BR", "ARGX.BR", "GBLB.BR", "KBC.BR", "UCB.BR", "UMIC.BR"
    ]
}

# --- FONCTION SCORE ---
def calculate_score(row):
    score = 0
    try:
        pe = float(row['P/E Ratio'])
        roe = float(row['ROE (%)'])
        debt = float(row['Dette/Equity (%)'])
        if 0 < pe < 15: score += 4
        elif 15 <= pe < 22: score += 2
        if roe > 15: score += 4
        elif roe > 10: score += 2
        if debt < 50: score += 2
    except: pass
    return score

def fetch_data(ticker):
    try:
        s = yf.Ticker(ticker)
        inf = s.info
        curr = inf.get('currentPrice') or inf.get('regularMarketPrice')
        if not curr: return None
        return {
            "Ticker": ticker,
            "Nom": inf.get('longName', ticker),
            "Secteur": inf.get('sector', 'Inconnu'),
            "Prix": curr,
            "P/E Ratio": inf.get('trailingPE'),
            "P/Book": inf.get('priceToBook'),
            "ROE (%)": (inf.get('returnOnEquity', 0) * 100) if inf.get('returnOnEquity') else 0,
            "Dette/Equity (%)": inf.get('debtToEquity', 0),
            "Yield (%)": (inf.get('dividendYield', 0) * 100) if inf.get('dividendYield') else 0
        }
    except: return None

# --- UI ---
st.title("🇪🇺 Equity Intelligence Europe Pro")

indices_selected = st.multiselect("Sélectionner les zones à analyser", list(TICKERS_DATA.keys()), default=["FRANCE (SBF 120 + LARGE SMALL CAPS)"])

if st.button("LANCER LE SCAN EUROPÉEN", type="primary"):
    all_tickers = []
    for idx in indices_selected:
        all_tickers.extend(TICKERS_DATA[idx])
    
    # Nettoyage doublons
    all_tickers = list(set(all_tickers))
    
    with st.spinner(f"Analyse de {len(all_tickers)} sociétés en cours..."):
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            data = list(filter(None, executor.map(fetch_data, all_tickers)))
        
        if data:
            df = pd.DataFrame(data).drop_duplicates(subset=['Ticker']).set_index("Ticker")
            # Conversion forcée pour éviter l'erreur de formatage
            for col in ['Prix', 'P/E Ratio', 'P/Book', 'ROE (%)', 'Dette/Equity (%)', 'Yield (%)']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['Score'] = df.apply(calculate_score, axis=1)
            st.session_state['eu_data'] = df

if 'eu_data' in st.session_state:
    df_f = st.session_state['eu_data'].fillna(0).copy()
    
    st.sidebar.header("⚙️ FILTRES")
    min_score = st.sidebar.slider("Score Minimum", 0, 10, 0)
    pb_limit = st.sidebar.checkbox("Isoler P/Book < 1")
    
    df_f = df_f[df_f['Score'] >= min_score]
    if pb_limit:
        df_f = df_f[df_f['P/Book'] < 1]

    # KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sociétés", len(df_f))
    c2.metric("Score Max", f"{int(df_f['Score'].max())}/10")
    c3.metric("P/B Moyen", round(df_f['P/Book'].mean(), 2))
    c4.metric("ROE Moyen", f"{round(df_f['ROE (%)'].mean(), 1)}%")

    # Tableau
    st.write("### 📋 Résultats de l'Analyse Fondamentale")
    st.dataframe(
        df_f.sort_values('Score', ascending=False).style.background_gradient(subset=['Score'], cmap='RdYlGn')
        .format({
            "Prix": "{:.2f} €", "P/E Ratio": "{:.1f}", "P/Book": "{:.2f}",
            "ROE (%)": "{:.1f}%", "Yield (%)": "{:.2f}%", "Dette/Equity (%)": "{:.1f}%"
        }),
        use_container_width=True
    )

    # Export
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_f.to_excel(writer, sheet_name='Europe_Screener')
    st.download_button("📥 EXPORTER VERS EXCEL", buf.getvalue(), "Screener_Europe.xlsx")