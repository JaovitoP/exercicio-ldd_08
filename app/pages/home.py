
import streamlit as st
from utils.aoi import *
from utils.catalog import *
from utils.indices import *
from utils.raster import read, transforme_20m
#from utils.statistics import *
from utils.visualization import *
import tempfile
import os

import zipfile

from datetime import datetime

import rasterio


st.title('Página Inicial')

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
                show_map(aoi)

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


if 'aoi' in st.session_state is not None:
    items = search_items(aoi, init_date, end_date)
    details = show_details(items)
    options = [
        {
            "label": f"Imagem [{i}]: Data: {datetime.fromisoformat(item.properties.get('datetime').replace('Z', '+00:00')).strftime('%d/%m/%Y')}, "
                     f"Cobertura de nuvens: {item.properties.get('eo:cloud_cover', 'N/A')}%, ",
            "item": item
        }
        for i, item in enumerate(items)
    ]

    labels = [opt["label"] for opt in options]

    img_pre_label = st.selectbox("Selecione a imagem Pré-Fogo", labels)
    img_pos_label = st.selectbox("Selecione a imagem Pós-Fogo", labels)

    imagem_pre = next(opt["item"] for opt in options if opt["label"] == img_pre_label)
    imagem_pos = next(opt["item"] for opt in options if opt["label"] == img_pos_label)

    thumbnail_pre = imagem_pre.assets['PVI'].href
    thumbnail_pos = imagem_pos.assets['PVI'].href

    columns = st.columns(2)
    with columns[0]:
        st.image(thumbnail_pre, caption=img_pre_label)
    with columns[1]:
        st.image(thumbnail_pos, caption=img_pos_label)

    st.header('Índices Espectrais')
    
    ds = rasterio.open(imagem_pre.assets['B04'].href)
    b04_pre,b04_pre_transf = read(imagem_pre.assets['B04'].href, bbox=aoi.total_bounds)
    b08_pre,b08_pre_transf = read(imagem_pre.assets['B08'].href, bbox=aoi.total_bounds)
    b8A_pre,_ = read(imagem_pre.assets['B8A'].href, bbox=aoi.total_bounds)
    b11_pre,_ = read(imagem_pre.assets['B11'].href, bbox=aoi.total_bounds)
    b12_pre,_ = read(imagem_pre.assets['B12'].href, bbox=aoi.total_bounds)
    _, box_trasform_20m = read(imagem_pre.assets['SCL'].href, bbox=aoi.total_bounds)

    b04_pre = transforme_20m(b04_pre,b04_pre_transf,ds.crs ) 
    b08_pre = transforme_20m(b08_pre,b08_pre_transf,ds.crs ) 

    #ler imagens pós fogo
    b04_pos,b04_pos_transf = read(imagem_pos.assets['B04'].href, bbox=aoi.total_bounds)
    b08_pos,b08_pos_transf = read(imagem_pos.assets['B08'].href, bbox=aoi.total_bounds)
    b8A_pos,_ = read(imagem_pos.assets['B8A'].href, bbox=aoi.total_bounds)
    b11_pos,_ = read(imagem_pos.assets['B11'].href, bbox=aoi.total_bounds)
    b12_pos,_ = read(imagem_pos.assets['B12'].href, bbox=aoi.total_bounds)

    #imagens pós-fogo
    b04_pos = transforme_20m(b04_pos,b04_pos_transf,ds.crs ) 
    b08_pos = transforme_20m(b08_pos,b08_pos_transf,ds.crs )

    rgb_pre = np.dstack([b12_pre, b08_pre, b04_pre])
    rgb_pos = np.dstack([b12_pos, b08_pos, b04_pos])

    plot_pre_pos(
        rgb_pre,
        rgb_pos
    )

    ndvi_pre = ndvi(b08_pre,b04_pre)
    nbr_pre = nbr(b8A_pre,b12_pre)
    nbrswir_pre = nbrswir(b11_pre,b12_pre)

        
    ndvi_pos = ndvi(b08_pos,b04_pos)
    nbr_pos = nbr(b8A_pos,b12_pos)
    nbrswir_pos = nbrswir(b11_pos,b12_pos)

    st.subheader('Índice de Vegetação por Diferença Normalizada (NDVI)')

    plot_ndvi(
        ndvi_pre,
        ndvi_pos,
    )

    st.subheader('NBR')


    plot_nbr(
        nbr_pre,
        nbr_pos,
    )

    st.subheader('NBRSWIR')


    plot_nbrswir(
        nbrswir_pre,
        nbrswir_pos,
    )


