#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import numpy as np

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

import rasterio
from rasterio import Affine
from rasterio.crs import CRS
#import rasterio.transform
from rasterio.windows import from_bounds
from rasterio.warp import Resampling, reproject, transform
from IPython.display import display, HTML

def show_collections(catalogo):
    for colecao in catalogo.get_collections():
        print(f"{colecao.title}: {colecao.id}", end="\n"*2)


# In[ ]:


def show_details(items):
    for i, item in enumerate(items):
        item_id = item.id  # ID do item para identificação
    
        date = item.properties.get('datetime', 'N/A')  # Data da aquisição
        
        cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')  # Obtém a cobertura de nuvens
        
        tile_id = items[0].properties.get('tileId')
            
        print(
            f"Imagem [{i}]: {item_id}," 
            f"Data: {date}," 
            f"Cobertura de nuvens: {cloud_cover:.1f}%," 
            f"Tile_ID: {tile_id}"
            )


# In[ ]:


def compare_images(thumbnail_pre, thumbnail_pos):
    # Dados dos thumbnails
    
    # Datas e títulos
    data_pre = thumbnail_pre.properties.get('datetime', 'N/A')[:10]
    data_pos = thumbnail_pos.properties.get('datetime', 'N/A')[:10]
    
    titulo_pre = f"Imagem pré-fogo - data: {data_pre}"
    titulo_pos = f"Imagem pós-fogo - data: {data_pos}"
    
    # HTML com títulos e imagens lado a lado
    html_code = f"""
    <div style="display: flex; align-items: flex-start;">
        <div style="text-align: center; margin-right: 20px;">
            <div style="font-weight: bold; margin-bottom: 5px;">{titulo_pre}</div>
            <img src="{thumbnail_pre.href}">
        </div>
        <div style="text-align: center;">
            <div style="font-weight: bold; margin-bottom: 5px;">{titulo_pos}</div>
            <img src="{thumbnail_pos.href}">
        </div>
    </div>
    """
    
    display(HTML(html_code))


# In[ ]:


def transforme_20m (asset, transforme, crs):
    '''Reamostragem de dados de 20 para 10 mts'''

    tranform_20 = Affine(20.0, 0.0, transforme.c,
                         transforme.d,-20.0,transforme.f)

    # Cria uma matriz numpy (grade regular) para o resultado reamostrado, com as dimensões (shape) e o tipo corretos
    array_20 = np.zeros((int(asset.shape[0]/2), int(asset.shape[1]/2)), dtype=asset.dtype)

    reproject(
        source=asset.data, # Passa apenas os valores e não o masked array
        destination=array_20,
        src_transform=transforme,
        src_crs=crs,
        dst_transform=tranform_20,
        dst_crs=crs,
        src_nodata=0, # Assume 0 como nodata para os dados de entrada
        dst_nodata=0, # Assume 0 como nodata para os dados de saída
        resampling=Resampling.nearest
    )
    return array_20


# In[ ]:


def read(uri: str, bbox: list, masked: bool = True, crs: str = None):
    """Read raster window as numpy.ma.masked_array."""
    source_crs = CRS.from_string('EPSG:4326')
    
    if crs:
        source_crs = CRS.from_string(crs)

    # Expects the bounding box has 4 values
    w, s, e, n = bbox
        
    with rasterio.open(uri) as dataset:
        transformer = transform(source_crs, dataset.crs, [w, e], [s, n])
        window = from_bounds(transformer[0][0], transformer[1][0], 
                             transformer[0][1], transformer[1][1], dataset.transform)
        
        box_trasform = rasterio.transform.from_bounds(transformer[0][0], transformer[1][0],
                                                      transformer[0][1], transformer[1][1], window.width, window.height)
        
        return dataset.read(1, window=window, masked=masked)*0.0001, box_trasform


# In[ ]:


def save_rgb_in_geotiff_format(crs, transform, *args):
    for img_index, image in enumerate(args):
        height, width, num_bands = image.shape

        file_name = f'./output/rgb_image{img_index}.tif'
        
        with rasterio.open(
            file_name,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=num_bands,
            dtype=image.dtype,
            crs=crs,
            transform=transform
        ) as dst:
            
            for band_index in range(num_bands):
                dst.write(image[:, :, band_index], band_index + 1)
        
        print(f'Imagem salva como {file_name}.')
    

# In[ ]:

def plot_pre_pos(rgb_pre, rgb_pos, 
                 title1="Pré-Fogo", 
                 title2="Pós-Fogo",
                 figsize=(10, 5)
                ):
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    axes[0].set_title(title1)
    axes[0].axis('off')
    axes[0].imshow((rgb_pre * 255).astype(np.uint8), interpolation='nearest')

    axes[1].set_title(title2)
    axes[1].axis('off')
    axes[1].imshow((rgb_pos * 255).astype(np.uint8), interpolation='nearest')

    plt.tight_layout()
    plt.show()

def plot_nbr(nbr_pre, nbr_pos, 
                 title1="Pré-Fogo", 
                 title2="Pós-Fogo",
                 figsize=(10, 5)
            ):
    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plota imagem NBR pré-fogo
    nbr_pre_plot = axes[0].imshow(nbr_pre, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[0].set_title(title1)
    axes[0].axis("off")
    cbar_pre = plt.colorbar(nbr_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBR Value")
    
    # Plota imagem NBR pós-fogo
    nbr_pos_plot = axes[1].imshow(nbr_pos, cmap="RdYlGn", vmin=-0.35, vmax=0.35, interpolation='nearest')
    axes[1].set_title(title2)
    axes[1].axis("off")
    cbar_pos = plt.colorbar(nbr_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBR Value")
    
    # Ajusta o layout para evitar sobreposição
    plt.tight_layout()
    plt.show()
    
    return

def plot_nbrswir(nbrswir_pre, nbrswir_pos, 
                 title1="Pré-Fogo", 
                 title2="Pós-Fogo",
                 figsize=(10, 5)):

    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plota imagem NBR pré-fogo
    nbrswir_pre_plot = axes[0].imshow(nbrswir_pre, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[0].set_title(title1)    
    axes[0].axis("off")
    cbar_pre = plt.colorbar(nbrswir_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NBRSWIR Value")
    
    # Plota imagem NBR pós-fogo
    nbrswir_pos_plot = axes[1].imshow(nbrswir_pos, cmap="RdYlGn", vmin=-0.15, vmax=0.15, interpolation='nearest')
    axes[1].set_title(title2)
    axes[1].axis("off")
    cbar_pos = plt.colorbar(nbrswir_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NBRSWIR Value")
    
    # Ajusta o layout para evitar sobreposição
    plt.tight_layout()
    plt.show()
    
    return


# In[ ]:


# Geração do Índice NDVI - Exemplo com bandas específicas do Sentinel
# NDVI = (B08 - B04) / (B08 + B04)

def ndvi(b08,b04):
    ndvi=(b08-b04)/(b08+b04)
    return ndvi

# Geração do Índice NBR
# NBR = (B08 - B12) / (B08 + B12)

def nbr(b8A,b12):
    nbr=(b8A-b12)/(b8A+b12)
    return nbr

# Geração do Índice NBRSWIR (Normalized Burn Ratio-SWIR)
# NBRSWIR = (B12 − B11 − 0.02)/( B12 + B11 + 0.1)

def nbrswir(b12,b11):
    nbrswir = (b12 - b11 - 0.02)/(b12 + b11 + 0.1)
    return nbrswir


# In[ ]:


# Total de detecções por dia
def show_detections_per_day(df):
    total_por_dia = df.groupby('data').size().reset_index(name='Total de detecções').rename(columns={'data':'Data'})
    
    display(total_por_dia)

