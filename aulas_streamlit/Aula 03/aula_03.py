import streamlit as st
import numpy as np
import pandas as pd

# Título
st.title('Trabalhando com Dados e Gráficos')

# Cabeçalho
st.header('Gerando e Exibindo dados aleatórios')

# Gerar um DataFrame

df = pd.DataFrame(
    np.random.randn(20, 3), # gerando um gráfico com 10 linhas e 3 colunas
    columns = ['a', 'b', 'c']
)

# Exibir o gráfico de forma interativa
st.subheader('Aqui é um gráfico gerado aleatoriamente')

st.dataframe(df)

# É possível exibir uma tabbela com st.table(), porém não é interativa (não dá para filtrar, esticar o tamanho etc)
st.table(df)

# Exibindo os gráficos
st.subheader('Gráficos simples com dados')
st.line_chart(df)
st.bar_chart(df)

# Exemplo com upload de arquivo
st.subheader('Carregando dados de arquio csv')

upload = st.file_uploader(
    label="Escolha um arquivo csv",
    type='csv'
)

if upload is not None:
    try:
        # Exibindo um pedaço do arquivo
        df_upload = pd.read_csv(upload)
        st.success('Arquivo carregado com sucesso!')
        st.write('As primeiras 5 linhas do seu arquivo:')
        st.dataframe(df_upload.head())

        # Tentar plotar as duas primeiras colunas, se existirem
        if df_upload.shape[1] >= 2:
            st.subheader('Gráfico das duas primeiras colunas')
            st.line_chart(df_upload.iloc[:, :2])
        else:
            st.info('Seu arquivo tem menos de duas colunas')
    except Exception as e:
        st.error(f'Erro ao carregar o arquivo: {e}. Certifique-se de que é um arquivo CSV válido.')