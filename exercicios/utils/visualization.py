import numpy as np
import matplotlib.pyplot as plt

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



def plot_ndvi(ndvi_pre, ndvi_pos,
                 title1="Pré-Fogo", 
                 title2="Pós-Fogo",
                 figsizee=(10,5)
             ):
    # Configura a figura com dois subplots (1 linha, 2 colunas)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plota imagem NBR pré-fogo
    ndvi_pre_plot = axes[0].imshow(ndvi_pre, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[0].set_title("NDVI - Data: 27-08-2025 - Pré Fogo")
    axes[0].axis("off")
    cbar_pre = plt.colorbar(ndvi_pre_plot, ax=axes[0], fraction=0.03, pad=0.04)
    cbar_pre.set_label("NDVI Value")
    
    # Plota imagem NBR pós-fogo
    ndvi_pos_plot = axes[1].imshow(ndvi_pos, cmap="RdYlGn", vmin=-0.2, vmax=0.65, interpolation='nearest')
    axes[1].set_title("NDVI - Data: 28-09-2025 - Pós Fogo")
    axes[1].axis("off")
    cbar_pos = plt.colorbar(ndvi_pos_plot, ax=axes[1], fraction=0.03, pad=0.04)
    cbar_pos.set_label("NDVI Value")
    
    # Ajusta o layout para evitar sobreposição
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
    
    return   plt.show()