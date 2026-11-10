import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Gestione Finanze", layout="wide")

st.title("💰 Gestione Finanze")

df = pd.read_csv("transactions.csv")

entrate = df[df["type"] == "income"]["amount"].sum()
uscite = df[df["type"] == "expense"]["amount"].sum()
saldo = entrate - uscite

col1, col2, col3 = st.columns(3)

col1.metric("Entrate", f"€ {entrate:,.2f}")
col2.metric("Uscite", f"€ {uscite:,.2f}")
col3.metric("Saldo", f"€ {saldo:,.2f}")

st.subheader("Movimenti")

st.dataframe(df)

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
