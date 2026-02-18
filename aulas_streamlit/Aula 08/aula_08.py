# pip freeze > requirements.txt

import streamlit as st

st.title('Calculadora')

st.sidebar.header('Sidebar')

colunas = st.columns(2)

num_1 = st.number_input(
    label = 'Digite o primeiro número',
    format='%0f'
)

num_2 = st.number_input(
    label = 'Digite o segundo número',
    format='%0f'
)

colunas = st.columns(4)

with colunas[0]:
    if st.button(label='Soma', use_container_width=True):
        resultado = num_1 + num_2
        st.text(f'Resultado: {resultado}')
with colunas[1]:
    if st.button(label='Subtração', use_container_width=True):
        resultado = num_1 - num_2
        st.text(f'Resultado: {resultado}')
with colunas[2]:
    if st.button(label='Multiplicação', use_container_width=True):
        resultado = num_1 * num_2
        st.text(f'Resultado: {resultado}')
with colunas[3]:
    if st.button(label='Divisão', use_container_width=True):
        resultado = num_1 / num_2
        st.text(f'Resultado: {resultado}')