import streamlit as st
import requests
import plotly.express as px

from src.api import buscar_historico, buscar_comparacao
from src.cores import cor_por_moeda
from src.config import MOEDAS, MOEDAS_EXIBICAO
from src.transformacoes import normalizar_base100

st.set_page_config(page_title="Crypto Dashboard", page_icon="📈", layout="wide")
st.title("📈 Crypto Dashboard")
st.caption("Dados da API pública CoinGecko")

# --- Sidebar ---
with st.sidebar:
    st.header("Filtros")
    moeda_nome = st.selectbox("Moeda", list(MOEDAS.keys()))
    moeda_exib_nome = st.selectbox("Moeda de exibição", list(MOEDAS_EXIBICAO.keys()))
    comparar_com = st.multiselect(
        "Comparar com",
        options=[m for m in MOEDAS.keys() if m != moeda_nome],
        default=[],
        placeholder="Escolha uma criptomoeda",
        help="Selecione moedas para comparar performance (base 100).",
    )
    dias = st.select_slider(
        "Período",
        options=[7, 30, 90, 365],
        value=30,
        format_func=lambda d: f"{d} dias" if d < 365 else "1 ano",
    )

moeda_id = MOEDAS[moeda_nome]
moeda_exib = MOEDAS_EXIBICAO[moeda_exib_nome]
simbolo = moeda_exib["simbolo"]
cor = cor_por_moeda(moeda_id)

# --- Busca dados ---
try:
    df = buscar_historico(moeda_id, dias, moeda_exib["codigo"])
except requests.HTTPError as e:
    if e.response is not None and e.response.status_code == 429:
        st.warning("⏳ Limite de requisições da API atingido.")
        if st.button("Tentar novamente"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error(f"Erro na API: {e}")
    st.stop()
except requests.RequestException as e:
    st.error(f"Não foi possível conectar à API: {e}")
    st.stop()

# --- Métricas ---
preco_atual = df["preco"].iloc[-1]
preco_inicial = df["preco"].iloc[0]
variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço atual", f"{simbolo} {preco_atual:,.2f}")
col2.metric("Variação no período", f"{variacao:+.2f}%")
col3.metric("Máxima no período", f"{simbolo} {df['preco'].max():,.2f}")
col4.metric("Mínima no período", f"{simbolo} {df['preco'].min():,.2f}")

# --- Gráfico de preço ---
fig = px.line(
    df,
    x="data",
    y="preco",
    title=f"Preço do {moeda_nome} em {moeda_exib_nome} (últimos {dias} dias)",
    labels={"data": "Data", "preco": f"Preço ({simbolo})"},
    color_discrete_sequence=[cor],
)
fig.update_layout(hovermode="x unified")
fig.update_traces(line=dict(width=3))
st.plotly_chart(fig, use_container_width=True)

# --- Comparação ---
if comparar_com:
    ids_comparacao = [moeda_id] + [MOEDAS[m] for m in comparar_com]
    try:
        df_comp = buscar_comparacao(ids_comparacao, dias, moeda_exib["codigo"])
    except requests.HTTPError as e:
        st.error(f"Erro ao buscar comparação: {e}")
    else:
        df_comp = normalizar_base100(df_comp)
        nomes = {v: k for k, v in MOEDAS.items()}
        df_comp["nome"] = df_comp["moeda"].map(nomes)

        st.info(
            "📊 **Como ler o gráfico abaixo:** cada moeda começa em 100 no primeiro dia. "
            "Uma linha em 120 significa valorização de 20% no período; em 80, queda de 20%. "
            "Assim dá para comparar moedas de preços muito diferentes (ex: BTC e DOGE) de forma justa."
        )

        fig_comp = px.line(
            df_comp,
            x="data",
            y="preco_norm",
            color="nome",
            title=f"Comparação de performance (base 100) — {dias} dias",
            labels={"data": "Data", "preco_norm": "Performance (base 100)", "nome": "Moeda"},
            color_discrete_map={nomes[mid]: cor_por_moeda(mid) for mid in ids_comparacao},
        )
        fig_comp.update_layout(hovermode="x unified")
        fig_comp.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)

        for trace in fig_comp.data:
            mask = df_comp["nome"] == trace.name
            trace.customdata = df_comp.loc[mask, "preco"].values
            trace.hovertemplate = (
                f"<b>{trace.name}</b><br>"
                f"Performance: %{{y:.1f}}<br>"
                f"Preço: {simbolo} %{{customdata:,.2f}}<extra></extra>"
            )

        st.plotly_chart(fig_comp, use_container_width=True)

# --- Volume ---
fig_vol = px.bar(
    df,
    x="data",
    y="volume",
    title=f"Volume de negociação do {moeda_nome} ({dias} dias)",
    labels={"data": "Data", "volume": f"Volume ({simbolo})"},
    color_discrete_sequence=[cor],
)
fig_vol.update_layout(hovermode="x unified", showlegend=False)
st.plotly_chart(fig_vol, use_container_width=True)

# --- Download CSV ---
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar dados em CSV",
    data=csv,
    file_name=f"{moeda_id}_{moeda_exib['codigo']}_{dias}d.csv",
    mime="text/csv",
)

# --- Tabela ---
with st.expander("Ver dados brutos"):
    st.dataframe(df.tail(20).iloc[::-1], use_container_width=True)