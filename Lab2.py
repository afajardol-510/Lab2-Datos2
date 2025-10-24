import pandas as pd
import networkx as nx
import math
import folium
from funciones import acciones
import webbrowser
import os


CSV_PATH = r"flights_final.csv"
OUTPUT_MAP = "mapa_aeropuertos.html"

# calcular distancia (fórmula de haversine)
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2]) #conviertiendo cada posición de grados a radianes
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 6371 * 2 * math.asin(math.sqrt(a))
    return c #distancia en kilometros entre los puntos

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

lista_comp = [] #Lista de los vértices que pertenecen a cada componente
recorrido = acciones(G) #Instancia de la clase RecorridosGrafo para usar la función

#CONEXIVIDAD DEL GRAFO
def componentes():
    raiz = list(G.nodes())[0] #Primer nodo del grafo

    componente1, vertices_comp =  recorrido.recorridoBFS(raiz) #Llamado a la función para recorrer el grafo por primera vez
    cantidad_nodos1 = sum(componente1.values()) #Calculo de la cantidad de nodos que tiene la primera componente
    lista_comp.append(vertices_comp) #Añadir a la lista de componente la primera componente
    conexo = True #Definir la conexidad como verdadera

    #Comparar la cantidad de vertices del primer componente con la cantidad de vértices en total del grafo
    #Si las cantidades son diferentes, significa que el grafo no es conexo

    if cantidad_nodos1 != G.number_of_nodes(): 
        print("El grafo no es conexo")

    cantidad_nodos = cantidad_nodos1 #Inicializar la cantidad de nodos
    last_comp = componente1 #Inicializar el último componente

    #Hacer el recorrido del grafo hasta encontrar todas las componentes
    #Cuando la cantidad de los nodos visitados sea igual a la cantidad de los nodos del grafo,se detiene


    while cantidad_nodos != G.number_of_nodes():
        #Encontrar el próximo vértice sin visitar para utilizarlo como raíz
        no_visitado = next((n for n, v in last_comp.items() if not v), None) 
        if no_visitado is None:
            break 
        #Llamado a la función para recorrer el grafo sin inicializar el vector visit
        new_comp, vertices_comp =  recorrido.recorridoBFS2(no_visitado, last_comp)
        lista_comp.append(vertices_comp) #Añadir a la lista de componentes la lista de los vértices de la nueva componente
        last_comp = new_comp #Asignar como última componente la nueva componente
        

def conexidad():
     #Mostrar la cantidad de componentes
    lista_comp.clear()
    componentes()
    cont = 1
    for l in lista_comp:
        print("Componente ",cont, ": ", len(l))
        cont += 1

def expansion_minima():   
    lista_comp.clear()
    componentes()     
    cont = 1
    for l in lista_comp:
        v_inicial = l[0]      # el primer vértice del componente
        mst = recorrido.prim(v_inicial)
        print("Peso del árbol de expansión mínima del componente ", cont)
        print(mst)
        cont += 1

def informacion():
    origen = input("Código del aeropuerto de origen: ").strip().upper()

    if origen not in G.nodes:
        print("Ese aeropuerto no existe en el grafo.")
    else:

        data_origen = G.nodes[origen]

        print(f"""
        Aeropuerto de origen:
        Código: {origen}
        Nombre: {data_origen['name']}
        Ciudad: {data_origen['city']}
        País: {data_origen['country']}
        Latitud: {data_origen['lat']:.3f}
        Longitud: {data_origen['lon']:.3f}
        """)

        nodos, dist, pad = recorrido.dijkstra(origen)

        nodos_validos = []
        dist_validas = []
        for i in range(len(nodos)):
            if dist[i] < math.inf:
                nodos_validos.append(nodos[i])
                dist_validas.append(dist[i])

        #Ordenamiento de las distancias en oreden descendente (Burbuja)
        for i in range(len(dist_validas) - 1):
            for j in range(len(dist_validas) - i - 1):
                if dist_validas[j] < dist_validas[j + 1]:
                    # Intercambiar distancias
                    dist_validas[j], dist_validas[j + 1] = dist_validas[j + 1], dist_validas[j]
                    # Intercambiar nodos
                    nodos_validos[j], nodos_validos[j + 1] = nodos_validos[j + 1], nodos_validos[j]

        print(f"\nLos 10 aeropuertos más lejanos desde {origen}:")

        for i in range(min(10, len(nodos_validos))):
            code = nodos_validos[i]
            d = dist_validas[i]
            data = G.nodes[code]
            print(f"""
    Código: {code}
    Nombre: {data['name']}
    Ciudad: {data['city']}
    País: {data['country']}
    Latitud: {data['lat']:.3f}
    Longitud: {data['lon']:.3f}
    Distancia: {d:.2f} km
    """)


def camino_minimo(self, origen, destino, camino):
    # Obtener las coordenadas promedio de todos los aeropuertos para centrar el mapa
        lats = [G.nodes[n]['lat'] for n in G.nodes]
        lons = [G.nodes[n]['lon'] for n in G.nodes]
        center = (sum(lats) / len(lats), sum(lons) / len(lons))

        # Crear el mapa base
        m = folium.Map(location=center, zoom_start=2)

        # Dibujar todos los aeropuertos como puntos azules
        for n, d in G.nodes(data=True):
            folium.CircleMarker(
                location=(d['lat'], d['lon']),
                radius=3,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=f"{d['name']} ({n})"  # Muestra el nombre y el código del aeropuerto
            ).add_to(m)

        # Si hay un camino válido, dibujarlo en rojo
        coordenadas_camino = [(G.nodes[c]['lat'], G.nodes[c]['lon']) for c in camino]
        folium.PolyLine(
            locations=coordenadas_camino,
            color='red',
            weight=3,
            opacity=0.8,
            tooltip=f"Camino mínimo: {origen} → {destino}"
        ).add_to(m)

        # Guardar el mapa como archivo HTML y abrirlo en el navegador
        m.save(OUTPUT_MAP)
        webbrowser.open(f"file://{os.path.abspath(OUTPUT_MAP)}")


cont = 0
while cont == 0:
    print("Menú del grafo:")
    print("  1. Conexidad del grafo.")
    print("  2. Peso de los árboles de expansión mínima.")
    print("  3. Información de un vértice y sus 10 más lejanos vértices.")
    print("  4. Camino mínimo entre dos vértices")
    print("  5. Salir")
    try:
        op = int(input("Opción: "))
    except ValueError:
        print("Por favor ingrese un número válido.")
        continue


    if op == 1:
        conexidad()
    
    if op == 2:
        expansion_minima()


    if op == 3:
        informacion()

    
    if op == 4:
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
    
    #nodos, dist, pad = recorrido.dijkstra(origen)
    nodos, dist, prev = recorrido.dijkstra(vertice1)
    if dist[vertice2] == float('inf'):
        print(f"No existe camino entre {vertice1} y {vertice2}.")
    else:       
        print("La distancia es ", dist[vertice2])
        camino = recorrido.reconstruir_camino(prev, vertice1, vertice2)

