# Por padrão, as pessoas usam o nome desse arquivo como streamlit_app.py

import streamlit as st

# Criar o menu de navegação das páginas
pg = st.navigation(
    [
        st.Page('./pages/home.py', title='Página Inicial'),
        st.Page('./pages/segunda_pagina.py', title='Página 2'),
        st.Page('./pages/terceira_pagina.py', title='Página 3')
     ],
     position='top'
)
pg.run()