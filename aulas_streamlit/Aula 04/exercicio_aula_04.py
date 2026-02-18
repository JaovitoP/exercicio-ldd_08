import streamlit as st
from random import randint

if 'ultimo_numero' not in st.session_state:
    st.session_state.ultimo_numero = 'Nenhum número foi gerado'

st.write(f'Último número gerado: {st.session_state.ultimo_numero}')


def gerar_numero_aleatorio():
    num_gerado = randint(1, 100)
    st.write(f'Novo Número gerado: {num_gerado}')
    st.session_state.ultimo_numero = num_gerado


if st.button('Gerar'):
    num_gerado = randint(1, 100)
    st.write(f'Novo Número gerado: {num_gerado}')
    st.session_state.ultimo_numero = num_gerado