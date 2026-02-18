import numpy as np
import pandas as pd
import streamlit as st

upload = st.file_uploader(
    label='Selecione um arquivo CSV',
    type='csv'
)

if upload is not None:
    try:
        df_upload = pd.read_csv(upload)
        st.success('Arquivo carregado com sucesso!')
        st.write('As 5 primeiras linhas do seu arquivo:')
        st.dataframe(df_upload.head())
        st.line_chart(df_upload)
        st.bar_chart(df_upload)

        st.write('Exibindo gráifco de barras dos jornais')
        st.bar_chart(df_upload['Jornal'])
        st.write('Exibindo gráfico de linhas dos jornais')
        st.line_chart(df_upload['Jornal'])
    except Exception as e:
        st.error(f'Erro ao carregar o arquivo {e}. Certifique-se de que é um arquivo CSV válido.')