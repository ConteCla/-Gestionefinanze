import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Gestione Finanze",
    layout="wide"
)

# ==========================
# GOOGLE SHEETS
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

file = client.open_by_key(
    "1I66hss5URRD39FB9YmvIxC8T_IKxXx1szWmXiOjripo"
)

sheet = file.sheet1
settings_sheet = file.worksheet("Impostazioni")

# ==========================
# LOAD DATA
# ==========================

data = sheet.get_all_records()
settings_data = settings_sheet.get_all_records()

df = pd.DataFrame(data)
settings_df = pd.DataFrame(settings_data)

# ==========================
# TITLE
# ==========================

st.title("💰 Gestione Finanze")

# ==========================
# FORM NUOVO MOVIMENTO
# ==========================

with st.expander("➕ Aggiungi movimento"):

    data_movimento = st.date_input(
        "Data",
        value=date.today()
    )

    tipo = st.selectbox(
        "Tipo",
        ["income", "expense"]
    )

    categorie = [
        "Stipendio",
        "Bollette",
        "Affitto",
        "Spesa",
        "Benzina",
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
        "Banca",
        "Altro (scrivi tu)"
    ]

    categoria_selezionata = st.selectbox(
        "Categoria",
        categorie
    )

    if categoria_selezionata == "Altro (scrivi tu)":
        categoria = st.text_input(
            "Inserisci nuova categoria"
        )
    else:
        categoria = categoria_selezionata

    importo = st.number_input(
        "Importo",
        min_value=0.0,
        step=1.0
    )

    nota = st.text_input("Nota")

    if st.button("Salva movimento"):

        if categoria == "":
            st.warning("Inserisci una categoria")
        else:

            nuova_riga = [
                str(data_movimento),
                tipo,
                categoria,
                importo,
                nota
            ]

            sheet.append_row(nuova_riga)

            st.success("Movimento salvato!")

            st.rerun()

# ==========================
# DASHBOARD
# ==========================

if not df.empty:

    df.columns = df.columns.str.lower()
    df["amount"] = pd.to_numeric(df["amount"])

    patrimonio_iniziale = float(
        settings_df.loc[
            settings_df["chiave"] == "patrimonio_iniziale",
            "valore"
        ].iloc[0]
    )

    obiettivo_capitale = float(
        settings_df.loc[
            settings_df["chiave"] == "obiettivo_capitale",
            "valore"
        ].iloc[0]
    )

    # ==========================
    # IMPOSTAZIONI
    # ==========================

    st.subheader("⚙️ Impostazioni")

    nuovo_patrimonio = st.number_input(
        "Patrimonio iniziale (€)",
        value=float(patrimonio_iniziale),
        step=100.0
    )

    nuovo_obiettivo = st.number_input(
        "Obiettivo capitale (€)",
        value=float(obiettivo_capitale),
        step=1000.0
    )

    if st.button("💾 Salva impostazioni"):

        riga_patrimonio = settings_df.index[
            settings_df["chiave"] == "patrimonio_iniziale"
        ][0] + 2

        riga_obiettivo = settings_df.index[
            settings_df["chiave"] == "obiettivo_capitale"
        ][0] + 2

        settings_sheet.update_cell(
            riga_patrimonio,
            2,
            nuovo_patrimonio
        )

        settings_sheet.update_cell(
            riga_obiettivo,
            2,
            nuovo_obiettivo
        )

        st.success("Impostazioni salvate")

        st.rerun()

    entrate = df[df["type"] == "income"]["amount"].sum()
    uscite = df[df["type"] == "expense"]["amount"].sum()

    saldo = entrate - uscite

    patrimonio_attuale = patrimonio_iniziale + saldo

    mancante = max(
        0,
        obiettivo_capitale - patrimonio_attuale
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Entrate", f"€ {entrate:,.2f}")
    col2.metric("Uscite", f"€ {uscite:,.2f}")
    col3.metric("Saldo", f"€ {saldo:,.2f}")
    col4.metric("Patrimonio", f"€ {patrimonio_attuale:,.2f}")

    st.subheader("🎯 Obiettivo")

    col5, col6 = st.columns(2)

    col5.metric(
        "Obiettivo",
        f"€ {obiettivo_capitale:,.2f}"
    )

    col6.metric(
        "Mancano",
        f"€ {mancante:,.2f}"
    )

    st.subheader("📋 Movimenti")

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==========================
    # ELIMINA MOVIMENTO
    # ==========================

    st.subheader("🗑️ Elimina movimento")

    movimento_da_eliminare = st.selectbox(
        "Seleziona il movimento",
        df.index,
        format_func=lambda i: (
            f"{df.loc[i, 'date']} | "
            f"{df.loc[i, 'category']} | "
            f"€ {df.loc[i, 'amount']}"
        )
    )

    conferma = st.checkbox(
        "Confermo di voler eliminare il movimento"
    )

    if conferma and st.button("🗑️ Elimina selezionato"):

        numero_riga_sheet = movimento_da_eliminare + 2

        sheet.delete_rows(numero_riga_sheet)

        st.success("Movimento eliminato!")

        st.rerun()

    # ==========================
    # ENTRATE VS USCITE
    # ==========================

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

    # ==========================
    # SPESE PER CATEGORIA
    # ==========================

    spese_categoria = (
        df[df["type"] == "expense"]
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )

    if not spese_categoria.empty:

        fig2 = px.pie(
            spese_categoria,
            names="category",
            values="amount",
            title="🥧 Ripartizione Spese"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # ==========================
    # PATRIMONIO NEL TEMPO
    # ==========================

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df = df.dropna(subset=["date"])

    df["signed_amount"] = df.apply(
        lambda row: row["amount"]
        if row["type"] == "income"
        else -row["amount"],
        axis=1
    )

    df = df.sort_values("date")

    df["capital"] = patrimonio_iniziale + df["signed_amount"].cumsum()

    fig3 = px.line(
        df,
        x="date",
        y="capital",
        markers=True,
        title="📈 Andamento Patrimonio"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


else:

    st.info("Nessun dato presente.")
