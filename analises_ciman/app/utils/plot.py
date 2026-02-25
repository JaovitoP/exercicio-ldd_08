import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import pandas as pd
import streamlit as st

def plot_comparativo(df_focos, ano, clima_inicio, clima_fim, img=None):

    # 🔹 série do ano escolhido
    ano_df = df_focos[df_focos.index.year == ano]["focos"].copy()
    ano_df.index = ano_df.index.month

    # 🔹 definir climatologia (baseline)
    df_clima = df_focos[
        (df_focos.index.year >= clima_inicio) &
        (df_focos.index.year <= clima_fim)
    ]

    # 🔹 estatísticas mensais do período escolhido
    med_mes = df_clima["focos"].groupby(df_clima.index.month).mean()
    min_mes = df_clima["focos"].groupby(df_clima.index.month).min()
    max_mes = df_clima["focos"].groupby(df_clima.index.month).max()

    # 🔹 dataframe para plot
    df_plot = pd.DataFrame({
        str(ano): ano_df,
        'min': min_mes,
        'med': med_mes,
        'max': max_mes
    }).reindex(range(1, 13))

    # 🔹 gráfico
    fig, ax = plt.subplots(figsize=(12, 6))

    # barras (ano atual)
    ax.bar(df_plot.index, df_plot[str(ano)], color='black', width=0.3, alpha=0.6, label=str(ano))

    # linhas climatologia
    ax.plot(df_plot.index, df_plot['min'], marker='o', color='#46bdc6', label='mínimo')
    ax.plot(df_plot.index, df_plot['med'], marker='o', color='#fbbc04', label=f'média ({clima_inicio}-{clima_fim})')
    ax.plot(df_plot.index, df_plot['max'], marker='o', color='#ea4335', label='máximo')

    # meses
    meses_nome = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(meses_nome)

    # grade
    ax.grid(True, linewidth=0.3, linestyle='--', alpha=0.6)

    # títulos
    ax.set_title(f'Comparativo mensal no Brasil: {ano} vs climatologia ({clima_inicio}-{clima_fim})')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Quantidade de focos')

    ax.legend()

    if img is not None:
        # Adicionar a logo no canto superior esquerdo da figura
        # Calculando a posição em pixels para o canto superior esquerdo
        dpi = fig.get_dpi()
        fig_width_pixels = fig.get_figwidth() * dpi
        fig_height_pixels = fig.get_figheight() * dpi

        logo_width_pixels = img.shape[1]
        logo_height_pixels = img.shape[0]

        padding = 50 # pixels

        xo_logo = padding*2 # x-offset from left
        yo_logo = fig_height_pixels - logo_height_pixels - padding # y-offset from bottom

        fig.figimage(img, xo=xo_logo, yo=yo_logo, zorder=1, alpha=1)

        # Ajustar o layout para garantir que o logo não seja cortado
        plt.tight_layout(rect=[(logo_width_pixels + padding)/fig_width_pixels, 0, 1, 1])

    plt.show()

def plot_annual_graph(df_anual, media_anual, desvio_anual, ano_i, ano_f):
    img = mpimg.imread('assets/LogoQmdPeq .png')

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 12), sharex=True) # Increased figure height significantly

    df_anual.focos_ano.plot(kind="bar", ax=axes[0], color='indianred', label='Focos Anuais', title=f'Série Histórica de Focos de calor no Brasil - Climatologia {ano_i} - {ano_f}')
    axes[0].set_ylabel('Número de Focos')
    axes[0].grid(True, axis='y', linestyle='--', alpha=0.6) # Updated grid for axes[0]
    axes[0].axhline(media_anual, color='black', linestyle='--', label='Média Histórica de Focos') # Add horizontal line for mean
    # Add standard deviation range - Changed color to a lighter blue
    # Using get_xlim() to ensure the fill spans the entire x-axis of the plot
    x_min, x_max = axes[0].get_xlim()
    axes[0].fill_between([x_min, x_max], media_anual - desvio_anual, media_anual + desvio_anual, color='grey', alpha=0.2, label='±1 Desvio Padrão Histórico', zorder=0) # zorder=0 to place it behind bars and grid
    axes[0].legend()

    df_anual.z_anual.plot(kind="bar", ax=axes[1], color='black', alpha=0.5, title=f'Z-Score de Focos no Brasil - Climatologia {ano_i} - {ano_f}')
    axes[1].set_ylabel('Z-Score')
    axes[1].set_xlabel('Ano')
    axes[1].grid(True, axis='y', linestyle='--', alpha=0.6) # Updated grid for axes[1]
    axes[1].set_yticks([-4,-3,-2,-1,0,1,2,3,4]) # Corrected: use set_yticks directly on the axes object
    axes[1].axhspan(3, 4, facecolor='#A25353', alpha=0.7, zorder=0)
    axes[1].axhspan(2, 3, facecolor='#D0A9A9', alpha=0.7, zorder=0)
    axes[1].axhspan( 1, 2, facecolor='#E8D4D4', alpha=0.7, zorder=0)
    axes[1].axhspan(-1, 1, facecolor='#ffffff', alpha=0.7, zorder=0)
    axes[1].axhspan(-1, -2, facecolor='#C5E1D1', alpha=0.7, zorder=0)
    axes[1].axhspan(-2, -3, facecolor='#8AC2A2', alpha=0.7, zorder=0)
    axes[1].axhspan(-3, -4, facecolor='#468646', alpha=0.7, zorder=0)
    axes[1].set_ylim(-4, 4)

    # Create custom legend handles for Z-index significance
    legend_patches = [
        mpatches.Patch(color='black', alpha=0.5, label='Focos Anuais (Barras)'),
        mpatches.Patch(color='#468646', alpha=0.7, label='Z < -3: Muito abaixo da média'),
        mpatches.Patch(color='#8AC2A2', alpha=0.7, label='-3 ≤ Z < -2: Consideravelmente abaixo'),
        mpatches.Patch(color='#C5E1D1', alpha=0.7, label='-2 ≤ Z < -1: Moderadamente abaixo da média'),
        mpatches.Patch(color='#ffffff', alpha=0.7, label='-1 ≤ Z ≤ +1: Próximo à média'),
        mpatches.Patch(color='#E8D4D4', alpha=0.7, label='+1 < Z ≤ +2: Moderadamente acima da média'),
        mpatches.Patch(color='#D0A9A9', alpha=0.7, label='+2 < Z ≤ +3: Consideravelmente acima'),
        mpatches.Patch(color='#A25353', alpha=0.7, label='Z > +3: Muito acima da média')
    ]

    # Add the custom legend to the Z-index subplot with horizontal layout
    # Adjusted bbox_to_anchor to align to the left and ensure it's inside the figure
    axes[1].legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(0.0, -0.15),
                    fancybox=True, shadow=True, ncol=2, title='Significado do Z-Index')

    # Adicionar a logo à figura
    # Calculate position for bottom-right corner, with some padding in pixels
    dpi = fig.get_dpi()
    fig_width_pixels = fig.get_figwidth() * dpi
    fig_height_pixels = fig.get_figheight() * dpi

    logo_width_pixels = img.shape[1]
    logo_height_pixels = img.shape[0]

    padding = 20 # pixels

    xo_logo = fig_width_pixels - logo_width_pixels - padding
    yo_logo = padding

    fig.figimage(img, xo=xo_logo, yo=yo_logo, zorder=1, alpha=1)

    plt.tight_layout(rect=[0, (logo_height_pixels + padding)/fig_height_pixels, 1, 1]) # Adjust layout to make space for logo at bottom
    plt.subplots_adjust(hspace=0.1) # Adjust vertical spacing between subplots
    st.pyplot(fig)