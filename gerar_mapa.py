import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
import numpy as np
from datetime import datetime

print("Baixando dados de previsão...")

# 1. Configuração da grade geográfica para o Brasil
# Resolução de 2.5 graus para manter a URL da requisição leve e estável
lats = np.arange(-35, 6, 2.5)
lons = np.arange(-74, -32, 2.5)

grid_lats, grid_lons = np.meshgrid(lats, lons)
flat_lats = grid_lats.flatten()
flat_lons = grid_lons.flatten()

# Requisição à API pública do Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": flat_lats.tolist(),
    "longitude": flat_lons.tolist(),
    "daily": "precipitation_sum",
    "timezone": "America/Recife",
    "forecast_days": 3
}

resp = requests.get(url, params=params)

if resp.status_code != 200:
    raise RuntimeError(f"Erro na API Open-Meteo (Status {resp.status_code}): {resp.text}")

response = resp.json()

# Processa os dados de precipitação acumulada em 72h
precip_72h = []
for item in response:
    daily_precip = item.get('daily', {}).get('precipitation_sum', [0, 0, 0])
    precip_total = sum([p if p is not None else 0 for p in daily_precip])
    precip_72h.append(precip_total)

precip_grid = np.array(precip_72h).reshape(grid_lats.shape)

# 2. Configuração do Mapa com Cartopy
print("Gerando o mapa...")
fig = plt.figure(figsize=(10, 8), dpi=150)
ax = plt.axes(projection=ccrs.PlateCarree())

# Limites do mapa (foco no Brasil)
ax.set_extent([-75, -32, -35, 6], crs=ccrs.PlateCarree())

# Camadas geográficas
ax.add_feature(cfeature.LAND, facecolor='#f8fafc')
ax.add_feature(cfeature.OCEAN, facecolor='#e0f2fe')
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#334155')
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.7, edgecolor='#64748b')
ax.add_feature(cfeature.STATES, linewidth=0.4, edgecolor='#94a3b8')

# Interpolação e preenchimento de cores (Contorno Suave)
cf = ax.contourf(
    grid_lons, grid_lats, precip_grid,
    levels=[1, 5, 10, 20, 30, 50, 75, 100, 150],
    cmap='YlGnBu',
    transform=ccrs.PlateCarree(),
    extend='max'
)

# Barra de cores
cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02, shrink=0.7)
cbar.set_label('Precipitação Acumulada em 72h (mm)', fontsize=10, fontweight='bold', color='#1e293b')

# Título com data atualizada
data_hoje = datetime.now().strftime('%d/%m/%Y')
plt.title(f'Previsão de Precipitação Acumulada (Próximos 3 Dias)\nLIDAR/UFCG - Atualizado em: {data_hoje}', 
          fontsize=11, fontweight='bold', color='#002147', pad=12)

plt.tight_layout()
plt.savefig('previsao_brasil.png', bbox_inches='tight')
print("Mapa gerado e salvo com sucesso como 'previsao_brasil.png'!")
plt.tight_layout()
plt.savefig('previsao_brasil.png', bbox_inches='tight')
print("Mapa salvo com sucesso como 'previsao_brasil.png'!")
