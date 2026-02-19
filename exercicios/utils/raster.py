import pandas as pd
import os
import numpy as np

from IPython.display import Image
import warnings
warnings.filterwarnings("ignore")

import rasterio
from rasterio import Affine
from rasterio.crs import CRS
#import rasterio.transform
from rasterio.windows import from_bounds
from rasterio.warp import Resampling, reproject, transform
from IPython.display import display, HTML

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