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
patrimonio_sheet = file.worksheet("Patrimonio")
# ==========================
# LOAD DATA
# ==========================

data = sheet.get_all_records()
settings_data = settings_sheet.get_all_records()

df = pd.DataFrame(data)
settings_df = pd.DataFrame(settings_data)
patrimonio_data = patrimonio_sheet.get_all_records()
patrimonio_df = pd.DataFrame(patrimonio_data)
totale_asset = patrimonio_df["valore"].sum()
# ==========================
# TITLE
# ==========================

st.title("💰 Gestione Finanze")
st.subheader("🏦 Allocazione Patrimonio")


col1, col2 = st.columns([1, 2])

with col1:

    st.metric(
        "Patrimonio",
        f"€ {totale_asset:,.0f}"
    )

    for _, riga in patrimonio_df.iterrows():

        percentuale = (
            riga["valore"] / totale_asset * 100
            if totale_asset > 0
            else 0
        )

        st.write(
            f"**{riga['categoria']}** "
            f"€ {riga['valore']:,.0f} "
            f"({percentuale:.1f}%)"
        )

with col2:

    fig_asset = px.pie(
        patrimonio_df,
        names="categoria",
        values="valore",
        title="Ripartizione Patrimonio"
    )

    st.plotly_chart(
        fig_asset,
        use_container_width=True
    )
st.subheader("✏️ Aggiorna Asset")

asset_scelto = st.selectbox(
    "Categoria",
    patrimonio_df["categoria"]
)

valore_asset = st.number_input(
    "Nuovo valore",
    min_value=0.0,
    step=100.0
)

if st.button(
    "Salva movimento",
    key="salva_movimento"
):

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

        indice_banca = patrimonio_df[
            patrimonio_df["categoria"] == "Banca"
        ].index[0]

        valore_banca = float(
            patrimonio_df.loc[
                indice_banca,
                "valore"
            ]
        )

        if tipo == "income":
            nuovo_valore_banca = valore_banca + importo
        else:
            nuovo_valore_banca = valore_banca - importo

        patrimonio_sheet.update_cell(
            indice_banca + 2,
            2,
            nuovo_valore_banca
        )

        st.success("Movimento salvato!")

        st.rerun()
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

if st.button("Salva movimento", key="salva_movimento"):

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

            indice_banca = patrimonio_df[
                patrimonio_df["categoria"] == "Banca"
            ].index[0]

            valore_banca = float(
                patrimonio_df.loc[
                    indice_banca,
                    "valore"
                ]
            )

            if tipo == "income":
                nuovo_valore_banca = valore_banca + importo
            else:
                nuovo_valore_banca = valore_banca - importo

            patrimonio_sheet.update_cell(
                indice_banca + 2,
                2,
                nuovo_valore_banca
            )

            st.success("Movimento salvato!")

            st.rerun()

# ==========================
# DASHBOARD
# ==========================

if not df.empty:

    df.columns = df.columns.str.lower()
    df["amount"] = pd.to_numeric(df["amount"])


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

    nuovo_obiettivo = st.number_input(
        "Obiettivo capitale (€)",
        value=float(obiettivo_capitale),
        step=1000.0
    )

    if st.button("💾 Salva impostazioni"):

        riga_obiettivo = settings_df.index[
            settings_df["chiave"] == "obiettivo_capitale"
        ][0] + 2

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

    patrimonio_attuale = totale_asset

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
# PATRIMONIO NEL TEMPO + PREVISIONE
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

df["capital"] = totale_asset - saldo + df["signed_amount"].cumsum()

# Patrimonio reale
fig3 = px.line(
    df,
    x="date",
    y="capital",
    markers=True,
    title="📈 Andamento Patrimonio"
)
fig3.update_xaxes(
    tickformat="%d/%m/%Y"
)


st.plotly_chart(
    fig3,
    use_container_width=True
)

