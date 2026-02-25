
import streamlit as st
import rasterio
import tempfile
import os
import zipfile
import pandas as pd
from datetime import datetime

from utils.aoi import *
from utils.catalog import *
from utils.indices import *
from utils.raster import *
from utils.visualization import *

st.set_page_config(
    layout='wide',
    page_icon='🗺️'
)

st.logo(image='assets/logotipo_conjugado.svg')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("""
    <div class="blue-section">
        <img src="assets/logotipo_govbr.png">
        <p>COMUNICA BR | ACESSO À INFORMAÇÃO | PARTICIPE | LEGISLAÇÃO | ÓRGÃOS</p>
    </div>
""", unsafe_allow_html=True)

menu = {
    "Sistemas": ["Sistema 1", "Sistema 2"],
    "Dados": ["Download CSV", "API"],
    "Relatórios": ["Mensal", "Anual"],
    "Sobre": ["Institucional", "Equipe"]
}

logo_col, menu_col = st.columns([1, 3])

with logo_col:
    st.image(
        image="assets/logotipo_conjugado.svg",
        width=180,
    )

with menu_col:
    with st.container(horizontal=True, horizontal_alignment="right"):
        for item, opcoes in menu.items():
            with st.popover(item, type="tertiary"):
                for opcao in opcoes:
                    st.button(opcao, type="tertiary")

st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

with st.container(border = True):
    st.title('Área de interesse')
    st.subheader('Faça upload da área de interesse')

    uploaded_file = st.file_uploader(
        label='Selecione um arquivo zip',
        type=['zip']
    )

    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(uploaded_file, 'r') as shapefile_zip:
                shapefile_zip.extractall(tmpdir)
                shp_files = [f for f in shapefile_zip.namelist() if f.lower().endswith('.shp')]
                if not shp_files:
                    st.error("Nenhum .shp encontrado")
                else:
                    shapefile_path = os.path.join(tmpdir, shp_files[0])
                    aoi = load_aoi(shapefile_path)
                    aoi = normalize_aoi(aoi)
                    st.session_state['aoi'] = aoi
                    st.success("Área de interesse carregada com sucesso!")
                    df = pd.DataFrame(aoi)
                    st.dataframe(df)

                    with st.spinner(f'Gerando Mapa...'):
                        show_map(aoi)    


if 'aoi' in st.session_state:
    
    with st.container(border=True):

        st.subheader('Selecione o intervalo de tempo')

        columns = st.columns(2)

        with columns[0]:

            init_date = st.date_input(
                label='Selecione a data de início',
                value='2025-08-25'
            )

        with columns[1]:

            end_date = st.date_input(
                label='Selecione a data de fim',
                value='2025-09-30'
            )


        if st.button('Buscar Imagens'):
            with st.spinner(f'Procurando Imagens...'):
                st.session_state['items'] = search_items(
                    st.session_state['aoi'],
                    init_date,
                    end_date
                )
            items = get_items_with_aoi_within(st.session_state['aoi'], list(st.session_state['items']))
            st.session_state['items'] = items
            
        if 'items' in st.session_state:

            items = st.session_state['items']

            num_cols = 5
                
            cols = st.columns(num_cols)
            for index, item in enumerate(items):
                col = cols[index % num_cols]
                with col:
                    st.image(item.assets['PVI'].href, use_container_width=True, caption=f'Imagem {index}: {datetime.fromisoformat(item.properties.get('datetime').replace('Z', '+00:00')).strftime('%d/%m/%Y')} | Cobertura (%): {item.properties.get('eo:cloud_cover', 'N/A')}%')

            details = show_details(items)
            options = [
                {
                    "label": f"Imagem [{i}]: Data: {datetime.fromisoformat(item.properties.get('datetime').replace('Z', '+00:00')).strftime('%d/%m/%Y')}, "
                            f"Cobertura de nuvens: {item.properties.get('eo:cloud_cover', 'N/A')}%",
                    "item": item
                }
                for i, item in enumerate(items)
            ]

            labels = [opt["label"] for opt in options]

            select_img_cols = st.columns(2)

            with select_img_cols[0]:
                img_pre_label = st.selectbox("Selecione a imagem Pré-Fogo", labels)
            with select_img_cols[1]:
                img_pos_label = st.selectbox("Selecione a imagem Pós-Fogo", labels)

            img_pre = next(opt["item"] for opt in options if opt["label"] == img_pre_label)
            img_pos = next(opt["item"] for opt in options if opt["label"] == img_pos_label)
            st.session_state['img_pre'] = img_pre
            st.session_state['img_pos'] = img_pos

            thumbnail_pre = img_pre.assets['PVI'].href
            thumbnail_pos = img_pos.assets['PVI'].href

            columns = st.columns(4)
            with columns[1]:
                st.image(thumbnail_pre, caption=img_pre_label)
            with columns[2]:
                st.image(thumbnail_pos, caption=img_pos_label)


            if 'show_map_flag' not in st.session_state:
                st.session_state['show_map_flag'] = False

            with st.expander("Visualizar imagens no mapa"):
                show_selected_areas_on_map(st.session_state['aoi'], img_pre, img_pos)

    if 'img_pre' in st.session_state:
        with st.container(border=True):
            st.title('Índices Espectrais')

            if st.button('Gerar Índices Espectrais'):
                aoi = st.session_state['aoi']

                with st.status('Processando imagens...', expanded=True) as status:
                    
                    try:

                        status.write("🔎 Lendo bandas da imagem pré-fogo...")

                        ds = rasterio.open(img_pre.assets['B04'].href)
                        b04_pre,b04_pre_transf = read(img_pre.assets['B04'].href, bbox=aoi.total_bounds)
                        b08_pre,b08_pre_transf = read(img_pre.assets['B08'].href, bbox=aoi.total_bounds)
                        b8A_pre,_ = read(img_pre.assets['B8A'].href, bbox=aoi.total_bounds)
                        b11_pre,_ = read(img_pre.assets['B11'].href, bbox=aoi.total_bounds)
                        b12_pre,_ = read(img_pre.assets['B12'].href, bbox=aoi.total_bounds)
                        _, box_trasform_20m = read(img_pre.assets['SCL'].href, bbox=aoi.total_bounds)

                        status.write("🔄 Reprojetando bandas 10m para 20m...")

                        b04_pre = transforme_20m(b04_pre,b04_pre_transf,ds.crs ) 
                        b08_pre = transforme_20m(b08_pre,b08_pre_transf,ds.crs ) 

                        status.write("🔥 Lendo bandas da imagem pós-fogo...")
                        b04_pos,b04_pos_transf = read(img_pos.assets['B04'].href, bbox=aoi.total_bounds)
                        b08_pos,b08_pos_transf = read(img_pos.assets['B08'].href, bbox=aoi.total_bounds)
                        b8A_pos,_ = read(img_pos.assets['B8A'].href, bbox=aoi.total_bounds)
                        b11_pos,_ = read(img_pos.assets['B11'].href, bbox=aoi.total_bounds)
                        b12_pos,_ = read(img_pos.assets['B12'].href, bbox=aoi.total_bounds)

                        status.write("🔄 Reprojetando pós-fogo...")
                        b04_pos = transforme_20m(b04_pos,b04_pos_transf,ds.crs ) 
                        b08_pos = transforme_20m(b08_pos,b08_pos_transf,ds.crs )

                        rgb_pre = np.dstack([b12_pre, b08_pre, b04_pre])
                        rgb_pos = np.dstack([b12_pos, b08_pos, b04_pos])


                        status.write("📊 Calculando índices espectrais...")
                        ndvi_pre = ndvi(b08_pre,b04_pre)
                        nbr_pre = nbr(b8A_pre,b12_pre)
                        nbrswir_pre = nbrswir(b11_pre,b12_pre)

                            
                        ndvi_pos = ndvi(b08_pos,b04_pos)
                        nbr_pos = nbr(b8A_pos,b12_pos)
                        nbrswir_pos = nbrswir(b11_pos,b12_pos)

                        ndvi_dif = ndvi_pre - ndvi_pos

                        nbr_dif = nbr_pre - nbr_pos

                        nbrswir_dif = nbrswir_pre - nbrswir_pos

                        status.update(label="✅ Processamento concluído!", state="complete")
                    except Exception as e:
                        status.write(f"❌ Erro: {e}")
                        status.update(label="Erro no processamento", state="error")



                indices = [
                    ("Área Queimada", lambda: plot_pre_pos(rgb_pre, rgb_pos)),
                    ("NDVI", lambda: plot_ndvi(ndvi_pre, ndvi_pos)),
                    ("NBR", lambda: plot_nbr(nbr_pre, nbr_pos)),
                    ("NBRSWIR", lambda: plot_nbrswir(nbrswir_pre, nbrswir_pos)),
                    ("Diferença entre índices", lambda: plot_difference_between_indices(ndvi_dif, nbr_dif, nbrswir_dif))
                ]

                num_cols = 2

                for i in range(0, len(indices), num_cols):
                    cols = st.columns(num_cols)

                    for col, (titulo, plot_func) in zip(cols, indices[i:i+num_cols]):
                        with col:
                            st.subheader(titulo)
                            with st.spinner(f'Gerando {titulo}...'):
                                plot_func()

                files = save_rgb_in_geotiff_format(ds.crs, box_trasform_20m, rgb_pre, rgb_pos)
                for file in files:
                    with open(file, 'rb') as f:
                        st.download_button(
                            label=f"Baixar {file.split('/')[-1]}",
                            data=f,
                            file_name=file.split('/')[-1],
                            mime="image/tiff"
                        )