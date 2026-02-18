import streamlit as st

st.title('Elementos interativos de layout')

# sidebar

st.sidebar.header('Opções da aplicação')

nome = st.sidebar.text_input(label='Digite o seu nome')
st.sidebar.text(f'Olá {nome}!')


# Colunas para organizar o contepudo principal

colunas = st.columns(2)

with colunas[0]:
    st.header('Interações simples')
    if st.button('Me aperte!'):
        st.success('Você clicou no botão!')
    valor_slider = st.slider(
        label="Selecione um valor",
        min_value=0,
        max_value=100,
        value=50
    )
    st.write(f'O valor selecionado é {valor_slider}.')

with colunas[1]:
    st.header('Informações e imagens')
    st.info('Esta é uma mensagem informativa.')

    # Você pode usar uma URL de imagem ou colocar o caminho do arquivo local
    st.image(
        image='https://miro.medium.com/0*BWuN8lNpH7zKKJ6d.jpg',
        caption='logo do Streamlit',
        use_container_width=True
    )

    st.image(
        image='image.jpeg',
        caption='tatuagem',
        use_container_width=True # usar todo o espaço do contianer (neste caso, a coluna)
    )
    st.warning('Atenção! Este é um aviso.')
    
    # Entrada de número e exibição
    numero = st.number_input(
        label='Digite um número',
        min_value=0,
        max_value=100
    ) 
    st.text(f'VocÊ digitou o número: {numero}')