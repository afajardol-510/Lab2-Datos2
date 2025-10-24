import pandas as pd
import networkx as nx
import math
import folium
import heapq
import tkinter as tk
from tkinter import messagebox
import webbrowser
import os

class Grafo:
    def __init__(self, nombre):
        self.nombre = nombre

    def dijkstra(self, G, start):
        dist = {node: float('inf') for node in G.nodes}
        prev = {node: None for node in G.nodes}
        dist[start] = 0
        pq = [(0, start)]

        while pq:
            current_dist, current_node = heapq.heappop(pq)
            if current_dist > dist[current_node]:
                continue
            for neighbor in G.neighbors(current_node):
                weight = G[current_node][neighbor]['weight']
                new_dist = current_dist + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))

        return dist, prev   # <-- fuera del while


    def reconstruir_camino(self, prev, origen, destino):
        camino = []
        actual = destino
        while actual is not None:
            camino.insert(0, actual)
            actual = prev[actual]
        if camino[0] == origen:
            return camino
        else:
            return []
        
    def mostrar_camino_minimo(self, origen, destino, camino):
        # Crear mapa con el camino en rojo
        lats = [G.nodes[n]['lat'] for n in G.nodes]
        lons = [G.nodes[n]['lon'] for n in G.nodes]
        center = (sum(lats) / len(lats), sum(lons) / len(lons))
        m = folium.Map(location=center, zoom_start=2)

        # Aeropuertos normales
        for n, d in G.nodes(data=True):
            folium.CircleMarker(
                location=(d['lat'], d['lon']),
                radius=3,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=f"{d['name']} ({n})"
            ).add_to(m)

        # Camino mínimo en rojo
        coordenadas_camino = [(G.nodes[c]['lat'], G.nodes[c]['lon']) for c in camino]
        folium.PolyLine(
            locations=coordenadas_camino,
            color='red',
            weight=3,
            opacity=0.8,
            tooltip=f"Camino mínimo: {origen} → {destino}"
        ).add_to(m)

        m.save(OUTPUT_MAP)
        webbrowser.open(f"file://{os.path.abspath(OUTPUT_MAP)}")


CSV_PATH = os.path.join(os.path.dirname(__file__), "flights_final.csv")
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

grafo = Grafo("hola")
cont = 0
vertice1 = None
cont = 0
while cont == 0:
    print("Menú del grafo:")
    print("  1. Caminos mínimos.")
    print("  2. Salir.")
    try:
        op = int(input("Opción: "))
    except ValueError:
        print("Por favor ingrese un número válido.")
        continue

    if op == 1:
        while True:
            vertice1 = input("Digite el vértice de inicio: ").strip()
            vertice2 = input("Digite el vértice destino: ").strip()

            if vertice1 not in G.nodes and vertice2 not in G.nodes:
                print(f"Los vértices {vertice1} y {vertice2} no existen en el grafo.")
            elif vertice1 not in G.nodes:
                print(f"El vértice {vertice1} no existe en el grafo.")
            elif vertice2 not in G.nodes:
                print(f"El vértice {vertice2} no existe en el grafo.")
            else:
                break

        dist1, prev1 = grafo.dijkstra(G, vertice1)
        if dist1[vertice2] == float('inf'):
            print(f"No existe camino entre {vertice1} y {vertice2}.")
        else:
            
            print("La distancia es ", dist1[vertice2])
            camino = grafo.reconstruir_camino(prev1, vertice1, vertice2)
            
            print("\n>>>>>>> CAMINO MÍNIMO ")
            for i, codigo in enumerate(camino):
                datos = G.nodes[codigo]
                print(f"{i+1}. ({codigo}) - {datos['name']} | {datos['city']}, {datos['country']} | "
                    f"Lat: {datos['lat']:.3f}, Lon: {datos['lon']:.3f}")
                
            print("\n>>>>>>>")


            grafo.mostrar_camino_minimo(vertice1, vertice2, camino)

    elif op == 2:
        cont = 1
        print("Saliendo del programa...")
        
    else:
        print("Opción no válida.")
