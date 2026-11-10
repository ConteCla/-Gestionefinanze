import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(page_title="Gestione Finanze", layout="wide")

# ==========================
# GOOGLE SHEETS CONNECTION
# ==========================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1I66hss5URRD39FB9YmvIxC8T_IKxXx1szWmXiOjripo"
).sheet1

# ==========================
# LOAD DATA
# ==========================

data = sheet.get_all_records()

df = pd.DataFrame(data)

if not df.empty:
    df.columns = df.columns.str.lower()

# ==========================
# FORM NUOVO MOVIMENTO
# ==========================

st.title("💰 Gestione Finanze")

with st.expander("➕ Aggiungi movimento"):

    data_movimento = st.date_input(
        "Data",
        value=date.today()
    )

    tipo = st.selectbox(
        "Tipo",
        ["income", "expense"]
    )

    categoria = st.selectbox(
    "Categoria",
    [
        "Stipendio",
        "Bollette",
        "Affitto",
        "Spesa",
        "Benzina",
        "Puzzone",
        "Ristorante",
        "Viaggi",
        "Investimenti",
        "Tempo Libero",
        "Casa",
        "Sport",
        "Shopping",
        "Salute",
        "Mezzi di trasporto",
        "Regali",
        "Macchina",
        "Bar/merende",
        "Cellulare",
        "Barbiere",
        "Banca"
        "Altro"
    ]
)

    importo = st.number_input(
        "Importo",
        min_value=0.0,
        step=1.0
    )

    descrizione = st.text_input("Descrizione")

    if st.button("Salva movimento"):

        nuova_riga = [
            str(data_movimento),
            tipo,
            categoria,
            importo,
            descrizione
        ]

        sheet.append_row(nuova_riga)

        st.success("Movimento salvato!")

        st.rerun()

# ==========================
# DASHBOARD
# ==========================

if not df.empty:

    entrate = df[df["type"] == "income"]["amount"].sum()

    uscite = df[df["type"] == "expense"]["amount"].sum()

    saldo = entrate - uscite

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Entrate",
        f"€ {entrate:,.2f}"
    )

    col2.metric(
        "Uscite",
        f"€ {uscite:,.2f}"
    )

    col3.metric(
        "Saldo",
        f"€ {saldo:,.2f}"
    )

    st.subheader("📋 Movimenti")

    st.dataframe(
        df,
        use_container_width=True
    )

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

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.info("Nessun dato presente.")
