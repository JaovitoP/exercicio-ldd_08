
import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.functions import *
from utils.biomas import *
from utils.functions import *
from utils.plot import *

st.set_page_config(
    layout='wide',
    page_icon='🗺️'
)

st.logo(image='assets/logotipo_conjugado.svg')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("""
    <div class="blue-section">
        <img src="assets/logotipo_govbr.png">
        <p>COMUNICA BR | ACESSO À INFORMAÇÃO | PARTICIPE | LEGISLAÇÃO | ÓRGÃOS</p>
    </div>
""", unsafe_allow_html=True)

menu = {
    "Sistemas": ["Sistema 1", "Sistema 2"],
    "Dados": ["Download CSV", "API"],
    "Relatórios": ["Mensal", "Anual"],
    "Sobre": ["Institucional", "Equipe"]
}

logo_col, menu_col = st.columns([1, 3])

with logo_col:
    st.image(
        image="assets/logotipo_conjugado.svg",
        width=180,
    )

with menu_col:
    with st.container(horizontal=True, horizontal_alignment="right"):
        for item, opcoes in menu.items():
            with st.popover(item, type="tertiary"):
                for opcao in opcoes:
                    st.button(opcao, type="tertiary")

st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

st.title('Analise Ciman')

st.header('Analisador de focos')

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state['ano'] = st.selectbox(
        label="Selecione o ano",
        options=[2026, 2025, 2024],
    )
with col2:
    ano_i = st.selectbox(
        label="Selecione o ano de início",
        options=[2026, 2025, 2024]
    )

with col3:
    ano_f = st.selectbox(
        label="Selecione o ano de fim",
        options=[2026, 2025, 2024]
    )

dados_br = 'https://data.inpe.br/queimadas/portal/csv/download/historico-mensal/paises/brasil.csv'
df_focos = ajusta_serie_temporal( preparar_focos(dados_br) )
df_focos = df_focos[df_focos.index.year <  date.today().year].copy() #até ano anterior
df_focos_var, stats = calcula_z_index(df_focos, ano_i, ano_f) #Definir qual o período da climatologia
df_focos_var = df_focos_var.drop(columns=['mean', 'mes', 'std'])

tabela = tabela_relatorio(df_focos_var, stats, st.session_state['ano'])

num_cols = tabela.select_dtypes(include='number').columns

st.dataframe(tabela)

df_anual, media_anual, desvio_anual = calcula_z_anual(df_focos, ano_i, ano_f)

plot_annual_graph(df_anual, media_anual, desvio_anual, ano_i, ano_f)