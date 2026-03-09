
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
from components.header import *

header()

if "show_ndvi" not in st.session_state:
    st.session_state.show_ndvi = False

if "show_nbr" not in st.session_state:
    st.session_state.show_nbr = False

if "show_nbrswir" not in st.session_state:
    st.session_state.show_nbrswir = False

if "show_diff" not in st.session_state:
    st.session_state.show_diff = False

with st.container(border = True):
    
    st.header("Desenhe sua Área de Interesse ou faça upload de um shapefile")

    with st.container(border=True):

        columns = st.columns(2)
        with columns[0]:

            m = create_map()

            map_data = st_folium(m, height=500, use_container_width=True)

            if map_data and map_data["all_drawings"]:
                draw_data = map_data["all_drawings"]

                aoi = drawing_to_gdf(draw_data)
                aoi = normalize_aoi(aoi)

                st.session_state['aoi'] = aoi

                st.success("AOI criada a partir do desenho!")
                st.dataframe(aoi)
        with columns[1]:

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

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.subheader("Índice de Vegetação por Diferença Normalizada (NDVI)")

                vmin_ndvi = st.number_input("vmin NDVI", value=-0.2, key="vmin_ndvi")
                vmax_ndvi = st.number_input("vmax NDVI", value=0.65, key="vmax_ndvi")

                if st.button('Gerar NDVI'):
                    st.session_state.show_ndvi = True

                if st.session_state.show_ndvi:
                    with st.spinner("Gerando NDVI..."):
                        plot_ndvi(ndvi_pre, ndvi_pos, vmin=vmin_ndvi, vmax=vmax_ndvi)

            with st.container(border=True):
                    st.subheader("NBRSWIR")
                    vmin_nbrswir = st.number_input("vmin NBRSWIR", value=-0.15, key="vmin_nbrswir")
                    vmax_nbrswir = st.number_input("vmax NBRSWIR", value=0.15, key="vmax_nbrswir")

                    if st.button('Gerar NBRSWIR'):
                        st.session_state.show_nbrswir = True

                    if st.session_state.show_nbrswir:
                        with st.spinner("Gerando NBRSWIR..."):
                            plot_nbrswir(nbrswir_pre, nbrswir_pos, vmin=vmin_nbrswir, vmax=vmax_nbrswir)


        with col2:
            with st.container(border=True):
                st.subheader("Índice de Queimada Normalizada (NBR)")

                vmin_nbr = st.number_input("vmin NBR", value=-0.35, key="vmin_nbr")
                vmax_nbr = st.number_input("vmax NBR", value=0.35, key="vmax_nbr")

                if st.button('Gerar NBR'):
                    st.session_state.show_nbr = True

                if st.session_state.show_nbr:
                    with st.spinner("Gerando NBR..."):
                        plot_nbr(nbr_pre, nbr_pos, vmin=vmin_nbr, vmax=vmax_nbr)


        with st.container(border=True):
            st.subheader("Diferença entre índices")
            vmin_diff = st.number_input("vmin Diferença", value=-0.15, key="vmin_diff")
            vmax_diff = st.number_input("vmax Diferença", value=0.25, key="vmax_diff")

            if st.button('Gerar Diferença entre índices'):
                st.session_state.show_diff = True

            if st.session_state.show_diff:
                with st.spinner("Gerando Diferença entre índices..."):
                    plot_difference_between_indices(ndvi_dif, nbr_dif, nbrswir_dif, vmin=vmin_diff, vmax=vmax_diff)