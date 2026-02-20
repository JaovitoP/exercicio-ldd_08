import pystac_client

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
    items = sorted(items, key=lambda x: x.datetime)
    print(items)
    return items
    

def show_details(items):
    details = []
    for i, item in enumerate(items):
        item_id = item.id  # ID do item
        date = item.properties.get('datetime', 'N/A')  # Data da aquisição
        
        # Cobertura de nuvens
        cloud_cover = item.properties.get('eo:cloud_cover', 'N/A')
        if isinstance(cloud_cover, (float, int)):
            cloud_cover_str = f"{cloud_cover:.1f}%"
        else:
            cloud_cover_str = str(cloud_cover)
        
        # Tile_ID do próprio item
        tile_id = item.properties.get('tileId', 'N/A')
        
        # Adiciona à lista
        details.append(
            f"Imagem [{i}]: Data: {date}, Cobertura de nuvens: {cloud_cover_str}, Tile_ID: {tile_id}"
        )
    return details