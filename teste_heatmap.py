import os

import pandas as pd
import plotly.express as px

# Simulando alguns dados de postos
dados = {
    'posto': ['Posto A', 'Posto B', 'Posto C', 'Posto D'],
    'latitude': [-23.5505, -23.5510, -23.5520, -23.5530],
    'longitude': [-46.6333, -46.6340, -46.6350, -46.6360],
    'preco_revenda': [5.59, 5.39, 5.79, 5.49]
}
df = pd.DataFrame(dados)

fig = px.scatter_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    color="preco_revenda",
    hover_name="posto",
    hover_data=["preco_revenda"],
    size="preco_revenda",
    size_max=15,
    zoom=13,
    mapbox_style="open-street-map",
    title="Mapa de Postos - Preço por Localização"
)

fig.show()
