import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
import numpy as np
from datetime import datetime

print("Baixando dados de previsão...")

# 1. Requisição de dados de grade para o Brasil (Open-Meteo API)
lats = np.arange(-35, 6, 1.5)
lons = np.arange(-74, -32, 1.5)

grid_lats, grid_lons = np.meshgrid(lats, lons)
flat_lats = grid_lats.flatten()
flat_lons = grid_lons.flatten()

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": flat_lats.tolist(),
    "longitude": flat_lons.tolist(),
    "daily": "precipitation_sum",
    "timezone": "America/Recife",
    "forecast_days": 3
}

response = requests.get(url, params=params).json()

precip_72h = []
for item in response:
    precip_total = sum(item['daily']['precipitation_sum'])
    precip_72h.append(precip_total)

precip_grid = np.array(precip_72h).reshape(grid_lats.shape)

# 2. Configuração do Mapa com Cartopy
print("Gerando o mapa...")
fig = plt.figure(figsize=(10, 8), dpi=150)
ax = plt.axes(projection=ccrs.PlateCarree())

ax.set_extent([-75, -30, -35, 7], crs=ccrs.PlateCarree())

ax.add_feature(cfeature.LAND, facecolor='#f4f4f4')
ax.add_feature(cfeature.OCEAN, facecolor='#e0f2fe')
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black')
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.7, edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.4, edgecolor='gray')

cf = ax.contourf(
    grid_lons, grid_lats, precip_grid,
    levels=[1, 5, 10, 20, 30, 50, 75, 100, 150],
    cmap='YlGnBu',
    transform=ccrs.PlateCarree(),
    extend='max'
)

cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02, shrink=0.7)
cbar.set_label('Precipitação Acumulada em 72h (mm)', fontsize=10)

data_hoje = datetime.now().strftime('%d/%m/%Y')
plt.title(f'Previsão de Precipitação Acumulada (Próximos 3 Dias)\nAtualizado em: {data_hoje}', fontsize=12, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig('previsao_brasil.png', bbox_inches='tight')
print("Mapa salvo com sucesso como 'previsao_brasil.png'!")
