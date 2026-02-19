def show_collections(catalogo):
    for colecao in catalogo.get_collections():
        print(f"{colecao.title}: {colecao.id}", end="\n"*2)

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