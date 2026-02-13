import streamlit as st

# Título principal da página

st.title('Minha primeira aplicação Streamlit!')

# Cabeçalho
st.header('Bem-vindo ao mundo Streamlit!')

# Subcabeçalho
st.subheader('Vamos explorar essa ferramenta incrível!')

#  Texto genérico
st.write('Este é um texto simpples usando o st.write()')

# Texto formatado com Markdown
st.markdown('''
Este é um exemplo de **Markdown** no Streamlit.
Podemos usar **negrito**, *itálico*, e até mesmo **listas**:
* Item 1
* Item 2
            
''')

# Texto literal
# Por ser um texto literal, não funciona o negrito, itálico, etc
st.text('Este é um texto puro, sem formatação')