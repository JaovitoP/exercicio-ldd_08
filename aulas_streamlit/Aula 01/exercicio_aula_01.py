import streamlit as st

st.title('Meu Perfil')

# Cabeçalho com as boas vindas
st.header('Seja bem vindo ao meu site! 👋')

# Subcabeçalho com o nome
st.subheader('Sou o João!')

# Usar o st.markdown() para as informações do perfil
st.markdown('''
Tecnólogo em **Desenvolvimento de Software Multiplataforma** 🧑🏻‍💻 e Técnico em **Desenvolvimento de Sistemas**
Gosto muito de *Python* me *PHP*, utilizo eles para tudo!
As áreas que gosto de estudar são:
* Análise de dados;
* Inteligência artificial;
* Automação;
''')

# Usar o st.write()
st.write('Espero que tenha gostado do meu perfil!')