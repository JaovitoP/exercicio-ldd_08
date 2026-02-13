#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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


def save_rgb_in_geotiff_format(*args):
    for i, image in enumerate(args):
        height, width, num_bands = image.shape

        file_name = f'./output/rgb_image{i}.tif'
        
        with rasterio.open(
            file_name,   # nome do arquivo de saída
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=num_bands,            # 3 bandas RGB
            dtype=rgb_pre.dtype,
            crs=ds.crs,                    # sistema de referência (ex.: "EPSG:4326")
            transform=box_trasform_20m         # transform (georreferenciamento)
        ) as dst:
            for i in range(num_bands):
                dst.write(rgb_pre[:, :, i], i + 1)
        
        print(f'RGB Pré-Fogo salvo como {file_name}.')


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

