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
    page_icon="Designer.png",
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

if data:
    df = pd.DataFrame(data)
else:
    df = pd.DataFrame(
        columns=[
            "date",
            "type",
            "category",
            "amount",
            "note"
        ]
    )

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
    "Salva Asset",
    key="salva_asset"
):

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
        "Puzzone",
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
saldo = 0

if not df.empty:

    df.columns = df.columns.str.lower()
    df["amount"] = pd.to_numeric(df["amount"])
    df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

# ==========================
# FILTRO MESE/ANNO
# ==========================

st.subheader("📅 Filtro")

col_f1, col_f2 = st.columns(2)

anni_disponibili = sorted(
    df["date"].dt.year.dropna().unique(),
    reverse=True
)

mesi = {
    "Tutti": 0,
    "Gennaio": 1,
    "Febbraio": 2,
    "Marzo": 3,
    "Aprile": 4,
    "Maggio": 5,
    "Giugno": 6,
    "Luglio": 7,
    "Agosto": 8,
    "Settembre": 9,
    "Ottobre": 10,
    "Novembre": 11,
    "Dicembre": 12
}

anno_selezionato = col_f2.selectbox(
    "Anno",
    anni_disponibili
)

mese_nome = col_f1.selectbox(
    "Mese",
    list(mesi.keys())
)

df_filtrato = df[
    df["date"].dt.year == anno_selezionato
]

if mese_nome != "Tutti":

    df_filtrato = df_filtrato[
        df_filtrato["date"].dt.month == mesi[mese_nome]
    ]
    

        
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

    entrate = df_filtrato[
    df_filtrato["type"] == "income"]["amount"].sum()

    uscite = df_filtrato[
    df_filtrato["type"] == "expense"]["amount"].sum()

    saldo = entrate - uscite
    # ==========================
    # CONFRONTO MESE PRECEDENTE
    # ==========================

    mese_corrente = mesi.get(mese_nome, 0)

    if mese_corrente > 1:

        df_precedente = df[
            (df["date"].dt.year == anno_selezionato) &
            (df["date"].dt.month == mese_corrente - 1)
        ]

        entrate_precedenti = df_precedente[
            df_precedente["type"] == "income"
        ]["amount"].sum()

        uscite_precedenti = df_precedente[
            df_precedente["type"] == "expense"
        ]["amount"].sum()
        if entrate_precedenti > 0:
            variazione_entrate = (
                (entrate - entrate_precedenti)
                / entrate_precedenti
                * 100
            )
        else:
            variazione_entrate = 0

        if uscite_precedenti > 0:
            variazione_uscite = (
                (uscite - uscite_precedenti)
                / uscite_precedenti
                * 100
            )
        else:
            variazione_uscite = 0

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
    if entrate > 0:
        tasso_risparmio = (saldo / entrate) * 100
    else:
        tasso_risparmio = 0
    st.subheader("📊 Analisi del periodo")

    col_a, col_b = st.columns(2)

    col_a.metric(
    "Risparmio",
    f"€ {saldo:,.2f}"
    )

    col_b.metric(
    "Tasso di risparmio",
    f"{tasso_risparmio:.1f}%"
    )
    if tasso_risparmio >= 30:

        st.success(
            f"🔥 Eccellente! Stai risparmiando il {tasso_risparmio:.1f}% delle entrate."
        )

    elif tasso_risparmio >= 20:

        st.success(
            f"✅ Ottimo! Stai risparmiando il {tasso_risparmio:.1f}% delle entrate."
        )

    elif tasso_risparmio >= 10:

        st.warning(
            f"⚠️ Discreto. Stai risparmiando il {tasso_risparmio:.1f}% delle entrate."
        )

    else:

        st.error(
            f"🚨 Risparmio basso: {tasso_risparmio:.1f}%."
        )
        if mese_corrente > 1:

            st.subheader("📈 Confronto col mese precedente")

            c_prev1, c_prev2 = st.columns(2)

            c_prev1.metric(
                "Entrate",
                f"€ {entrate:,.0f}",
                f"{variazione_entrate:.1f}%"
            )

            c_prev2.metric(
                "Uscite",
                f"€ {uscite:,.0f}",
                f"{variazione_uscite:.1f}%"
            )
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
    df_filtrato,
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
        df_filtrato.groupby("type")["amount"]
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
        df_filtrato[df_filtrato["type"] == "expense"]
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
    # FISSE VS DESIDERI VS RISPARMIO
    # ==========================

    categorie_fisse = [
        "Affitto",
        "Bollette",
        "Cellulare",
        "Banca",
        "Spesa",
        "Benzina",
        "Casa",
        "Barbiere",
        "Mezzi di trasporto",
        "Macchina",
        "Puzzone",
        "Cellulare",
        "Salute"
    ]

    categorie_desideri = [
        "Ristorante",
        "Shopping",
        "Viaggi",
        "Tempo Libero",
        "Bar/merende",
        "Regali",
        "Sport"
    ]

    spese_fisse = df[
        (df["type"] == "expense") &
        (df["category"].isin(categorie_fisse))
    ]["amount"].sum()

    spese_desideri = df[
        (df["type"] == "expense") &
        (df["category"].isin(categorie_desideri))
    ]["amount"].sum()

    risparmio = max(0, saldo)

    analisi_df = pd.DataFrame({
        "Voce": [
            "Spese Fisse",
            "Desideri",
            "Risparmio"
        ],
        "Valore": [
            spese_fisse,
            spese_desideri,
            risparmio
        ]
    })

    fig_analisi = px.pie(
        analisi_df,
        names="Voce",
        values="Valore",
        title="🧠 Fisse vs Desideri vs Risparmio"
    )

    st.plotly_chart(
        fig_analisi,
        use_container_width=True
    )
# ==========================
# PATRIMONIO NEL TEMPO + PREVISIONE
# ==========================

if df.empty:

    st.info("Nessun movimento presente.")

else:

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

    df["capital"] = (
        totale_asset
        - saldo
        + df["signed_amount"].cumsum()
    )

    fig3 = px.line(
        df,
        x="date",
        y="capital",
        markers=True,
        title="📈 Andamento Patrimonio"
    )

    # ==========================
    # PREVISIONE
    # ==========================

    oggi = pd.Timestamp.today()

    mesi_passati = max(
        1,
        oggi.month
    )

    risparmio_medio = saldo / mesi_passati

    ultimo_capitale = df["capital"].iloc[-1]

    date_future = pd.date_range(
        start=pd.Timestamp(
            year=oggi.year,
            month=oggi.month + 1 if oggi.month < 12 else 12,
            day=1
        ),
        end=f"{oggi.year}-12-01",
        freq="MS"
    )

    capitale_previsto = ultimo_capitale

    capitali_previsti = []

    for _ in date_future:

        capitale_previsto += risparmio_medio

        capitali_previsti.append(
            capitale_previsto
        )

    if len(date_future) > 0:

        fig3.add_scatter(
            x=date_future,
            y=capitali_previsti,
            mode="lines+markers",
            name="Previsione",
            line=dict(
                color="orange",
                dash="dash",
                width=3
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
