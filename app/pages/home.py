
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

if "show_dnbrswir" not in st.session_state:
    st.session_state.show_dnbrswir = False

if "dnbrswir_and_mask" not in st.session_state:
    st.session_state.dnbrswir_and_mask = False

if 'aoi' not in st.session_state:
    st.session_state['aoi'] = None

with st.container(border = True):
    
    st.title(body =" Mapeamento de fogo", text_alignment="center")

    with st.container(border=True):
        st.subheader("Desenhe sua área de interesse no mapa ou faça o upload")

        if 'aoi_mode' not in st.session_state:
            st.session_state['aoi_mode'] = None

        st.markdown("### Selecione a área de interesse")

        col_btn1, col_btn2, col_spacer = st.columns([1, 1, 4])

        with col_btn1:
            if st.button("🖊️ Desenhar no Mapa", use_container_width=True,
                        type="primary" if st.session_state['aoi_mode'] == 'draw' else "secondary"):
                st.session_state['aoi_mode'] = 'draw'

        with col_btn2:
            if st.button("📁 Fazer Upload", use_container_width=True,
                        type="primary" if st.session_state['aoi_mode'] == 'upload' else "secondary"):
                st.session_state['aoi_mode'] = 'upload'

        if st.session_state['aoi_mode'] == 'draw':
            m = create_map()
            map_data = st_folium(m, height=500, use_container_width=True)

            if map_data and map_data["all_drawings"]:
                draw_data = map_data["all_drawings"]
                last_drawing = [draw_data[-1]]
                aoi = drawing_to_gdf(last_drawing)
                aoi = normalize_aoi(aoi)
                st.session_state['aoi'] = aoi
                st.success("AOI criada a partir do desenho!")
                st.dataframe(aoi)

        elif st.session_state['aoi_mode'] == 'upload':
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

            st.subheader('Intervalo de tempo')
            st.write('Selecione a data de início e a data de fim das imagens que deseja buscar.')

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
                if options:
                    st.subheader('Selecione a imagem pré e pós fogo para comparação e visualização de camadas no mapa.')

                    labels = [opt["label"] for opt in options]

                    select_img_cols = st.columns(4)

                    col_select, col_map = st.columns([1, 1])

                    with col_select:

                        select_img_cols = st.columns(2)


                        with select_img_cols[0]:
                            img_pre_label = st.selectbox("Selecione a imagem Pré-Fogo", labels)

                        img_pre = next(opt["item"] for opt in options if opt["label"] == img_pre_label)

                        with select_img_cols[1]:
                            img_pos_label = st.selectbox("Selecione a imagem Pós-Fogo", labels)

                        img_pos = next(opt["item"] for opt in options if opt["label"] == img_pos_label)

                        st.session_state['img_pre'] = img_pre
                        st.session_state['img_pos'] = img_pos

                        thumbnail_pre = img_pre.assets['PVI'].href
                        thumbnail_pos = img_pos.assets['PVI'].href

                        img_cols = st.columns(2)

                        with img_cols[0]:
                            st.image(thumbnail_pre, caption=img_pre_label)

                        with img_cols[1]:
                            st.image(thumbnail_pos, caption=img_pos_label)


                    with col_map:

                        if 'show_map_flag' not in st.session_state:
                            st.session_state['show_map_flag'] = False

                        with st.expander("Visualizar imagens no mapa", expanded=True):
                            show_selected_areas_on_map(
                                st.session_state['aoi'],
                                st.session_state['img_pre'],
                                st.session_state['img_pos']
                            )
                else:
                    st.warning("Nenhuma imagem encontrada para a área de interesse no intervalo de tempo selecionados.")



if 'img_pre' in st.session_state:
            with st.container(border=True):
                st.title('Índices Espectrais')

                aoi = st.session_state['aoi']
                img_pre = st.session_state['img_pre']
                img_pos = st.session_state['img_pos']

                imgs_key = (img_pre.id, img_pos.id)

                if st.session_state.get('processed_imgs_key') != imgs_key:
                    with st.status('Processando imagens...', expanded=True) as status:
                        try:
                            status.write("🔎 Lendo bandas da imagem pré-fogo...")
                            ds = rasterio.open(img_pre.assets['B04'].href)
                            b04_pre, b04_pre_transf = read(img_pre.assets['B04'].href, bbox=aoi.total_bounds)
                            b08_pre, b08_pre_transf = read(img_pre.assets['B08'].href, bbox=aoi.total_bounds)
                            b8A_pre, _ = read(img_pre.assets['B8A'].href, bbox=aoi.total_bounds)
                            b11_pre, _ = read(img_pre.assets['B11'].href, bbox=aoi.total_bounds)
                            b12_pre, _ = read(img_pre.assets['B12'].href, bbox=aoi.total_bounds)
                            _, box_trasform_20m = read(img_pre.assets['SCL'].href, bbox=aoi.total_bounds)

                            status.write("🔄 Reprojetando bandas 10m para 20m...")
                            b04_pre = transforme_20m(b04_pre, b04_pre_transf, ds.crs)
                            b08_pre = transforme_20m(b08_pre, b08_pre_transf, ds.crs)

                            status.write("🔥 Lendo bandas da imagem pós-fogo...")
                            b04_pos, b04_pos_transf = read(img_pos.assets['B04'].href, bbox=aoi.total_bounds)
                            b08_pos, b08_pos_transf = read(img_pos.assets['B08'].href, bbox=aoi.total_bounds)
                            b8A_pos, _ = read(img_pos.assets['B8A'].href, bbox=aoi.total_bounds)
                            b11_pos, _ = read(img_pos.assets['B11'].href, bbox=aoi.total_bounds)
                            b12_pos, _ = read(img_pos.assets['B12'].href, bbox=aoi.total_bounds)

                            status.write("🔄 Reprojetando pós-fogo...")
                            b04_pos = transforme_20m(b04_pos, b04_pos_transf, ds.crs)
                            b08_pos = transforme_20m(b08_pos, b08_pos_transf, ds.crs)

                            st.session_state['ndvi_pre']    = ndvi(b08_pre, b04_pre)
                            st.session_state['ndvi_pos']    = ndvi(b08_pos, b04_pos)
                            st.session_state['nbr_pre']     = nbr(b8A_pre, b12_pre)
                            st.session_state['nbr_pos']     = nbr(b8A_pos, b12_pos)
                            st.session_state['nbrswir_pre'] = nbrswir(b11_pre, b12_pre)
                            st.session_state['nbrswir_pos'] = nbrswir(b11_pos, b12_pos)
                            st.session_state['ndvi_dif']    = st.session_state['ndvi_pre'] - st.session_state['ndvi_pos']
                            st.session_state['nbr_dif']     = st.session_state['nbr_pre']  - st.session_state['nbr_pos']
                            st.session_state['nbrswir_dif'] = st.session_state['nbrswir_pre'] - st.session_state['nbrswir_pos']
                            st.session_state['processed_imgs_key'] = imgs_key

                            status.update(label="✅ Processamento concluído!", state="complete")
                        except Exception as e:
                            status.write(f"❌ Erro: {e}")
                            status.update(label="Erro no processamento", state="error")

                if st.session_state.get('processed_imgs_key') == imgs_key:
                    ndvi_pre    = st.session_state['ndvi_pre']
                    ndvi_pos    = st.session_state['ndvi_pos']
                    nbr_pre     = st.session_state['nbr_pre']
                    nbr_pos     = st.session_state['nbr_pos']
                    nbrswir_pre = st.session_state['nbrswir_pre']
                    nbrswir_pos = st.session_state['nbrswir_pos']
                    ndvi_dif    = st.session_state['ndvi_dif']
                    nbr_dif     = st.session_state['nbr_dif']
                    nbrswir_dif = st.session_state['nbrswir_dif']

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
                        st.subheader("Diferença entre os índices NDVI, NBR e NBR SWIR")
                        vmin_diff = st.number_input("vmin Diferença", value=-0.15, key="vmin_diff")
                        vmax_diff = st.number_input("vmax Diferença", value=0.25, key="vmax_diff")
                        if st.button('Gerar Diferença entre índices'):
                            st.session_state.show_diff = True
                        if st.session_state.show_diff:
                            with st.spinner("Gerando Diferença entre índices..."):
                                plot_difference_between_indices(
                                    ndvi_dif, nbr_dif, nbrswir_dif,
                                    vmin=vmin_diff, vmax=vmax_diff
                                )

                    col1, col2 = st.columns([1, 2])

                    with col1, st.container(border=True):
                        threshold = st.number_input("Threshold", value=0.06, key="threshold")
                        if st.button('Gerar dNBRswir'):
                            st.session_state.show_dnbrswir = True
                        if st.session_state.show_dnbrswir:
                            with st.spinner("Gerando dNBRswir..."):
                                plot_dnbrswir(nbrswir_dif, threshold)

                    with col2, st.container(border=True):
                        vmin_dnbrswir = st.number_input("vmin dNBRswir", value=-0.15, key="vmin_dnbrswir")
                        vmax_dnbrswir = st.number_input("vmax dNBRswir", value=0.25, key="vmax_dnbrswir")
                        if st.button('Gerar NBRswir e máscara'):
                            st.session_state.dnbrswir_and_mask = True
                        if st.session_state.dnbrswir_and_mask:
                            with st.spinner("Gerando dNBRswir e máscara..."):
                                plot_dnbrswir_and_mask(nbrswir_dif, threshold, vmin_dnbrswir, vmax_dnbrswir)