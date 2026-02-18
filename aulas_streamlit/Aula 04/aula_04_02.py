# Importar os módulos

import time
import streamlit as st

st.title('Otimizando com caching')

@st.cache_data(ttl=3600)
def simular_operacao_demorada(parametro):
    st.write(f'Executando operação demorada para o parâmetro: {parametro}')
    time.sleep(3)
    return f'Resultado da operação demorada para {parametro}: {time.time()}'


# Parâmetro
parametro = st.slider(
    label='Escolha um parâmetro',
    min_value=0,
    max_value=10,
    value=5
)

resultado = simular_operacao_demorada(parametro)
st.write(resultado)

# Botão para limpar o cache manualmente
st.button(
    label='Limpar cache',
    on_click=st.cache_data.clear
)