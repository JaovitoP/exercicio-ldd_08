import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import streamlit as st
from folium.plugins import MousePosition, MeasureControl, Fullscreen, HeatMap
from folium import Marker

from datetime import datetime

def show_map(aoi):
    f = folium.Figure()
    centro = aoi.geometry.centroid.iloc[0]
    mapa = folium.Map(location=[centro.y, centro.x],
               zoom_start=10,
               tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
               attr="Esri World Imagery"
        ).add_to(f)

    folium.GeoJson(aoi).add_to(mapa)

    MousePosition().add_to(mapa)

    mapa.add_child(MeasureControl())
    Fullscreen().add_to(mapa)

    st_folium(mapa, width="100%", height=600)

def show_selected_areas_on_map(aoi, imagem_pre, imagem_pos):
    f = folium.Figure()

    centro = aoi.geometry.centroid.iloc[0]
    center_lat, center_lon = centro.y, centro.x

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10).add_to(f)

    tif_img_pre = imagem_pre.assets['TCI'].href
    tif_img_pos = imagem_pos.assets['TCI'].href

    title_img_pre = datetime.fromisoformat(
        imagem_pre.properties['datetime']
    ).strftime("%d/%m/%y %H:%M")

    title_img_pos = datetime.fromisoformat(
        imagem_pos.properties['datetime']
    ).strftime("%d/%m/%y %H:%M")

    tms_url_1 = f"https://data.inpe.br/bdc/tms/tiles/WebMercatorQuad/{{z}}/{{x}}/{{y}}?url={tif_img_pre}"

    folium.TileLayer(
        tiles=tms_url_1,
        attr="INPE Sentinel-2",
        name=title_img_pre,
        overlay=True,
        control=True
    ).add_to(m)

    tms_url_2 = f"https://data.inpe.br/bdc/tms/tiles/WebMercatorQuad/{{z}}/{{x}}/{{y}}?url={tif_img_pos}"

    folium.TileLayer(
        tiles=tms_url_2,
        attr="INPE Sentinel-2",
        name=title_img_pos,
        overlay=True,
        control=True
    ).add_to(m)

    folium.GeoJson(
        aoi,
        name="AOI",
        style_function=lambda x: {
            'color': 'red',
            'weight': 2,
            'fill': False
        }
    ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width="100%", height=600)       

def plot_pre_pos(rgb_pre, rgb_pos):

    fig, axes = plt.subplots(
        1, 2,
        figsize=(14,7),
        constrained_layout=True
    )


    axes[0].axis('off')
    axes[0].imshow((rgb_pre * 255).astype(np.uint8), interpolation='nearest')
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")


    axes[1].axis('off')
    axes[1].imshow((rgb_pos * 255).astype(np.uint8), interpolation='nearest')

    st.pyplot(fig)
    plt.close(fig)


def plot_ndvi(ndvi_pre, ndvi_pos):
    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    
    # Plota imagem NBR pré-fogo
    ndvi_pre_plot = axes[0].imshow(ndvi_pre, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(ndvi_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NDVI Value")
    
    # Plota imagem NBR pós-fogo
    ndvi_pos_plot = axes[1].imshow(ndvi_pos, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(ndvi_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NDVI Value")
    
    # Ajusta o layout para evitar sobreposição
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    

def plot_nbr(nbr_pre, nbr_pos):
    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plota imagem NBR pré-fogo
    nbr_pre_plot = axes[0].imshow(nbr_pre, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(nbr_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBR Value")
    
    # Plota imagem NBR pós-fogo
    nbr_pos_plot = axes[1].imshow(nbr_pos, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(nbr_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBR Value")
    
    # Ajusta o layout para evitar sobreposição
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)


def plot_nbrswir(nbrswir_pre, nbrswir_pos):

    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plota imagem NBR pré-fogo
    nbrswir_pre_plot = axes[0].imshow(nbrswir_pre, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[0].axis("off")
    axes[0].set_title("Pré-Fogo", fontsize=14, fontweight="bold")
    cbar_pre = plt.colorbar(nbrswir_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBRSWIR Value")
    
    # Plota imagem NBR pós-fogo
    nbrswir_pos_plot = axes[1].imshow(nbrswir_pos, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[1].axis("off")
    axes[1].set_title("Pós-Fogo", fontsize=14, fontweight="bold")
    cbar_pos = plt.colorbar(nbrswir_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBRSWIR Value")
    
    # Ajusta o layout para evitar sobreposição
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)
