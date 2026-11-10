import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Gestione Finanze",
    layout="wide"
)

st.title("💰 Gestione Finanze")

# Google Sheet pubblicato come CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSt5GvPYQSg7aJltt1mYTOMPErsr95EAAtMfGO7TGzxYa86K_ZXGvZhXWf2olbHP3IjDb_niZ4oyT3m/pub?output=csv"

# Caricamento dati
df = pd.read_csv(SHEET_URL)

# Uniforma i nomi delle colonne
df.columns = df.columns.str.lower()

# KPI
entrate = df[df["type"] == "income"]["amount"].sum()
uscite = df[df["type"] == "expense"]["amount"].sum()
saldo = entrate - uscite

col1, col2, col3 = st.columns(3)

col1.metric("Entrate", f"€ {entrate:,.2f}")
col2.metric("Uscite", f"€ {uscite:,.2f}")
col3.metric("Saldo", f"€ {saldo:,.2f}")

# Tabella dati
st.subheader("📋 Movimenti")

st.dataframe(df, use_container_width=True)

# Grafico Entrate vs Uscite
grafico = (
    df.groupby("type")["amount"]
    .sum()
    .reset_index()
)

fig = px.bar(
    grafico,
    x="type",
    y="amount",
    color="type",
    title="Entrate vs Uscite"
)

st.plotly_chart(fig, use_container_width=True)
