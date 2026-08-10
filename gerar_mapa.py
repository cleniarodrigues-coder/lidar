import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
import numpy as np
from datetime import datetime

print("Baixando dados de previsão em lotes...")

# 1. Configuração da grade geográfica para o Brasil
lats = np.arange(-35, 6, 2.0)
lons = np.arange(-74, -32, 2.0)

grid_lats, grid_lons = np.meshgrid(lats, lons)
flat_lats = grid_lats.flatten().tolist()
flat_lons = grid_lons.flatten().tolist()

# Fazer requisições em lotes (batches) de no máximo 50 pontos por vez para evitar URL extensa (Erro 414)
batch_size = 50
precip_72h = []

url = "https://api.open-meteo.com/v1/forecast"

for i in range(0, len(flat_lats), batch_size):
    batch_lats = flat_lats[i:i + batch_size]
    batch_lons = flat_lons[i:i + batch_size]
    
    params = {
        "latitude": batch_lats,
        "longitude": batch_lons,
        "daily": "precipitation_sum",
        "timezone": "America/Recife",
        "forecast_days": 3
    }

    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        raise RuntimeError(f"Erro na API Open-Meteo (Status {resp.status_code}): {resp.text}")

    response = resp.json()

    # Tratamento caso retorne uma lista de locais ou um único objeto
    if isinstance(response, list):
        for item in response:
            daily_precip = item.get('daily', {}).get('precipitation_sum', [0, 0, 0])
            precip_total = sum([p if p is not None else 0 for p in daily_precip])
            precip_72h.append(precip_total)
    else:
        daily_precip = response.get('daily', {}).get('precipitation_sum', [0, 0, 0])
        precip_total = sum([p if p is not None else 0 for p in daily_precip])
        precip_72h.append(precip_total)

precip_grid = np.array(precip_72h).reshape(grid_lats.shape)

# 2. Configuração e plotagem do Mapa com Cartopy
print("Gerando o mapa...")
fig = plt.figure(figsize=(10, 8), dpi=150)
ax = plt.axes(projection=ccrs.PlateCarree())

# Limites do mapa focando no Brasil
ax.set_extent([-75, -32, -35, 6], crs=ccrs.PlateCarree())

# Camadas geográficas
ax.add_feature(cfeature.LAND, facecolor='#f8fafc')
ax.add_feature(cfeature.OCEAN, facecolor='#e0f2fe')
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#334155')
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.7, edgecolor='#64748b')
ax.add_feature(cfeature.STATES, linewidth=0.4, edgecolor='#94a3b8')

# Contorno de precipitação
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

# Título com identificação do laboratório e data
data_hoje = datetime.now().strftime('%d/%m/%Y')
plt.title(f'Previsão de Precipitação Acumulada (Próximos 3 Dias)\nLIDAR/UFCG - Atualizado em: {data_hoje}', 
          fontsize=11, fontweight='bold', color='#002147', pad=12)

plt.tight_layout()
plt.savefig('previsao_brasil.png', bbox_inches='tight')
print("Mapa gerado com sucesso e salvo como 'previsao_brasil.png'!")
