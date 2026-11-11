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

# ==========================
# TITLE
# ==========================

st.title("💰 Gestione Finanze")
st.subheader("🏦 Allocazione Patrimonio")

totale_asset = patrimonio_df["valore"].sum()

col1, col2 = st.columns([1, 2])

with col1:

    st.metric(
        "Patrimonio investito",
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

if st.button("Salva Asset"):

    indice = patrimonio_df[
        patrimonio_df["categoria"] == asset_scelto
    ].index[0]

    patrimonio_sheet.update_cell(
        indice + 2,
        2,
        valore_asset
    )

    st.success("Asset aggiornato")

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

df["capital"] = patrimonio_iniziale + df["signed_amount"].cumsum()

# Patrimonio reale
fig3 = px.line(
    df,
    x="date",
    y="capital",
    markers=True,
    title="📈 Andamento Patrimonio"
)

# ------------------
# PREVISIONE
# ------------------

oggi = pd.Timestamp.today()

mesi_passati = max(
    1,
    len(
        pd.date_range(
            start=f"{oggi.year}-01-01",
            end=oggi,
            freq="MS"
        )
    )
)

risparmio_medio_mensile = saldo / mesi_passati

ultimo_capitale = df["capital"].iloc[-1]

ultimo_giorno_reale = df["date"].max()

date_future = pd.date_range(
    start=ultimo_giorno_reale + pd.DateOffset(months=1),
    end=f"{oggi.year}-12-31",
    freq="MS"
)

capitali_previsti = []

capitale = ultimo_capitale

for _ in date_future:

    capitale += risparmio_medio_mensile

    capitali_previsti.append(capitale)

previsione_df = pd.DataFrame({
    "date": date_future,
    "capital": capitali_previsti
})

fig3.add_scatter(
    x=previsione_df["date"],
    y=previsione_df["capital"],
    mode="lines+markers",
    name="Previsione",
    line=dict(
        color="orange",
        dash="dash"
    )
)

fig3.update_xaxes(
    range=[
        f"{oggi.year}-01-01",
        f"{oggi.year}-12-31"
    ],
    dtick="M1",
    tickformat="%b"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

