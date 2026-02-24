import pystac_client
from shapely.geometry import shape
import geopandas as gpd
import streamlit as st
from shapely import wkt

def get_catalog():
    service='https://data.inpe.br/bdc/stac/v1/'
    catalog = pystac_client.Client.open(service)
    return catalog

def show_collections():
    catalog = get_catalog()
    for colecao in catalog.get_collections():
        print(f"{colecao.title}: {colecao.id}", end="\n"*2)

def search_items(aoi, init_date, end_date):
    print(aoi, init_date, end_date)
    
    catalog = get_catalog()
    
    collection = 'S2_L2A-1'
    date_range = f'{init_date}/{end_date}'
    item_search = catalog.search(bbox=aoi.total_bounds,
        collections=[collection],
        datetime=date_range
    )
    items = list(item_search.item_collection())
    items_within_aoi = get_items_with_aoi_within(aoi, items)
    items_within_aoi = sorted(items_within_aoi, key=lambda x: x.datetime)
    return items_within_aoi
    

def show_details(items):
    details = []
    for i, item in enumerate(items):
        item_id = item.id
        date = item.properties.get('datetime', 'N/A')
        
        cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
        if isinstance(cloud_cover, (float, int)):
            cloud_cover_str = f"{cloud_cover:.1f}%"
        else:
            cloud_cover_str = str(cloud_cover)
        
        tile_id = item.properties.get('tileId', 'N/A')
        
        details.append(
            f"Imagem [{i}]: Data: {date}, Cobertura de nuvens: {cloud_cover_str}, Tile_ID: {tile_id}"
        )
    return details


def get_items_with_aoi_within(aoi, items):
    aoi_geom = aoi.geometry.values[0]
    items_within_aoi = []
    
    for idx, item in enumerate(items):
        footprint_wkt = item.properties['Footprint']
        
        if "geography" in footprint_wkt:
            footprint_wkt = footprint_wkt.replace("geography'SRID=4326;", "")
        
        footprint_wkt = footprint_wkt.strip("'")
        
        try:
            footprint_geom = wkt.loads(footprint_wkt)
        except Exception as e:
            st.write(f"Erro ao carregar geometria WKT do item {idx + 1}: {e}")
            continue 
        
        
        if aoi_geom.within(footprint_geom):
            items_within_aoi.append(item)
    
    return items_within_aoi