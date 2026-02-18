import streamlit as st

st.title('Contador e estado da sessão')

# Inicializar o sessions_state se ainda não existir
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def incrementar_contador():
    st.session_state.contador += 1

# Mostrar valor atual do contador
st.write(f'O valor atual do contador é: {st.session_state.contador}')

# Aumentar o valor do contador
st.button(
    label='Incrementar contador',
    on_click=incrementar_contador # Se colocar entre parenteses vai executar assim que carregar a página
)

# Exemplo de formulário
st.header('Formulário com estado')

if 'nome_usuario' not in st.session_state:
    st.session_state.nome_usuario = ''

def atualizar_nome():
    st.session_state.nome_usuario = st.session_state.nome_usuario_input

st.text_input(
    label='Digite o nome',
    key='nome_usuario_input',
    on_change=atualizar_nome
)

st.write(f'Nome salvo: {st.session_state.nome_usuario}')
