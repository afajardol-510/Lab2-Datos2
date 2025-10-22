import pandas as pd
import networkx as nx
import math
import folium

CSV_PATH = r"C:\Users\anaec\OneDrive\Documentos\LAB2\flights_final.csv"
OUTPUT_MAP = "mapa_aeropuertos.html"

# calcular distancia (fórmula de haversine)
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 6371 * 2 * math.asin(math.sqrt(a))
    return c

print("Cargando dataset")
df = pd.read_csv(CSV_PATH)

print("Construyendo grafo")
G = nx.Graph()

for index, row in df.iterrows():
    try:
        src = row['Source Airport Code']
        dst = row['Destination Airport Code']

        lat1 = float(row['Source Airport Latitude'])
        lon1 = float(row['Source Airport Longitude'])
        lat2 = float(row['Destination Airport Latitude'])
        lon2 = float(row['Destination Airport Longitude'])

        dist = haversine(lat1, lon1, lat2, lon2)

        # agregar nodos
        G.add_node(src, name=row['Source Airport Name'], city=row['Source Airport City'],
                   country=row['Source Airport Country'], lat=lat1, lon=lon1)
        G.add_node(dst, name=row['Destination Airport Name'], city=row['Destination Airport City'],
                   country=row['Destination Airport Country'], lat=lat2, lon=lon2)

        # agregar arista (si no existe o si hay una más corta)
        if not G.has_edge(src, dst) or dist < G[src][dst]['weight']:
            G.add_edge(src, dst, weight=dist)
    except Exception:
        continue

print(f"Grafo creado con {G.number_of_nodes()} aeropuertos y {G.number_of_edges()} rutas.")

print("Generando mapa")

# calcular centro aproximado del mapa
lats = []
lons = []
for n in G.nodes:
    lats.append(G.nodes[n]['lat'])
    lons.append(G.nodes[n]['lon'])

center = (sum(lats) / len(lats), sum(lons) / len(lons))
m = folium.Map(location=center, zoom_start=2)

# agregar marcadores
for n, d in G.nodes(data=True):
    popup = f"""
    <b>{d.get('name', '')}</b><br>
    {d.get('city', '')}, {d.get('country', '')}<br>
    Código: {n}<br>
    Lat: {d.get('lat', 0):.3f}, Lon: {d.get('lon', 0):.3f}
    """
    folium.CircleMarker(
        location=(d['lat'], d['lon']),
        radius=3,
        popup=popup,
        color='blue',
        fill=True,
        fill_opacity=0.7
    ).add_to(m)

# guardar mapa
m.save(OUTPUT_MAP)
print(f"Mapa guardado en: {OUTPUT_MAP}")
