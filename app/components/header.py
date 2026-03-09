import streamlit as st

def header():
    st.set_page_config(
        layout='wide',
        page_icon='🗺️'
    )

    st.logo(image='assets/logotipo_conjugado.svg')

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    logo_col, menu_col = st.columns([1, 3])

    with logo_col:
        st.image(
            image="assets/logotipo_conjugado.svg",
            width=180,
        )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)