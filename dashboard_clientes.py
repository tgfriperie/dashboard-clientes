import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Escolha do arquivo via selectbox
arquivo_opcoes = {
    "Clientes com 1 Compra": "relatorio_clientes_1_compra.xlsx",
    "Clientes com Várias Compras": "relatorio_clientes_2_compra.xlsx"
}

st.set_page_config(page_title="Dashboard de Clientes", layout="wide")

st.title("Dashboard de Clientes")

with st.sidebar:
    st.header("Configurações")
    arquivo_selecionado = st.selectbox("Escolha o relatório para análise:", options=list(arquivo_opcoes.keys()))

# Carrega o arquivo Excel escolhido
arquivo = arquivo_opcoes[arquivo_selecionado]
df = pd.read_excel(arquivo)

# Estilo CSS igual antes
st.markdown(
    """
    <style>
    /* Fundo da sidebar e do app */
    .css-1d391kg {  /* sidebar */
        background-color: #f2f2f2 !important; /* color1 */
        color: #0a0c0d !important; /* color5 */
    }
    .css-18e3th9 {  /* app background */
        background-color: #f2f2f2 !important; /* color1 */
        color: #0a0c0d !important; /* color5 */
    }

    /* Títulos e textos */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
        color: #213635 !important; /* color4 */
    }

    /* Labels dos filtros na sidebar */
    label[data-baseweb="label"] {
        color: #1c5052 !important; /* color3 */
        font-weight: bold;
    }

    /* Botões */
    button {
        background-color: #348e91 !important; /* color2 */
        color: #f2f2f2 !important; /* color1 */
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        transition: background-color 0.3s ease;
    }
    button:hover {
        background-color: #1c5052 !important; /* color3 */
        color: #f2f2f2 !important;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.header(f"Analisando: {arquivo_selecionado}")

# 🎯 Filtros múltiplos
with st.sidebar:
    st.header("Filtros")
    anos = sorted(df['Ano da Última Compra'].dropna().unique())
    meses = sorted(df['Mês da Última Compra'].dropna().unique())
    tipos_pf_pj = df['Física / Jurídica'].dropna().unique()
    tipos_canal = df['Atacado / Varejo'].dropna().unique()

    anos_selecionados = st.multiselect("Ano", anos, default=anos)
    meses_selecionados = st.multiselect("Mês", meses, default=meses)
    tipo_pessoa = st.multiselect("Tipo de Cliente", tipos_pf_pj, default=tipos_pf_pj)
    canal = st.multiselect("Canal", tipos_canal, default=tipos_canal)

# 🧼 Aplica filtros
df_filtrado = df[
    (df['Ano da Última Compra'].isin(anos_selecionados)) &
    (df['Mês da Última Compra'].isin(meses_selecionados)) &
    (df['Física / Jurídica'].isin(tipo_pessoa)) &
    (df['Atacado / Varejo'].isin(canal))
]

# 🔢 Métricas principais
col1, col2 = st.columns(2)
with col1:
    st.metric("🧍‍♂️ Total de Clientes", int(df_filtrado['Qtd_Clientes'].sum()))
with col2:
    st.metric("💸 Ticket Médio Geral", f"R$ {df_filtrado['Ticket_Medio'].mean():.2f}")

# 📈 Gráfico novo: Crescimento de Clientes por Ano
df_ano = df_filtrado.groupby('Ano da Última Compra', as_index=False).agg({
    'Qtd_Clientes': 'sum'
})

fig_ano = px.bar(
    df_ano,
    x='Ano da Última Compra',
    y='Qtd_Clientes',
    title="📈 Crescimento de Clientes por Ano",
    labels={'Qtd_Clientes': 'Quantidade de Clientes', 'Ano da Última Compra': 'Ano'}
)

st.plotly_chart(fig_ano, use_container_width=True)

# 📈 Gráfico 1: Clientes por Mês/Ano
df_group = df_filtrado.groupby(['Ano da Última Compra', 'Mês da Última Compra'], as_index=False).agg({
    'Qtd_Clientes': 'sum',
    'Ticket_Medio': 'mean'
})

fig1 = px.bar(
    df_group,
    x='Mês da Última Compra',
    y='Qtd_Clientes',
    color='Ano da Última Compra',
    barmode='group',
    title="Quantidade de Clientes por Mês/Ano"
)

# 📈 Gráfico 2: Ticket Médio por Mês/Ano
fig2 = px.line(
    df_group,
    x='Mês da Última Compra',
    y='Ticket_Medio',
    color='Ano da Última Compra',
    markers=True,
    title="💸 Ticket Médio por Mês/Ano"
)

# Exibe os gráficos antigos
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# 📋 Exibe tabela
st.subheader("Tabela de Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# 💾 Botão de download
def gerar_excel_download(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Clientes Filtrados')
    buffer.seek(0)
    return buffer

excel_bytes = gerar_excel_download(df_filtrado)

st.download_button(
    label="⬇Baixar dados filtrados em Excel",
    data=excel_bytes,
    file_name=f"clientes_filtrados_{arquivo_selecionado.replace(' ', '_').lower()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
