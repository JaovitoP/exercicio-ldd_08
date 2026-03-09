import geopandas as gpd
import json

def load_aoi(shapefile):
    return gpd.read_file(shapefile)

def normalize_aoi(aoi):
    return aoi.to_crs(4326)

def drawing_to_gdf(draw_data):
    geojson = {
        "type": "FeatureCollection",
        "features": draw_data
    }

    gdf = gpd.GeoDataFrame.from_features(geojson, crs="EPSG:4326")
    return gdf