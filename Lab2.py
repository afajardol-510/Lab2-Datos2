import pandas as pd
import networkx as nx
import math
import folium
from funciones import acciones
import webbrowser
import os


CSV_PATH = r"flights_final.csv"
OUTPUT_MAP = "mapa_aeropuertos.html"
OUTPUT_AML = "aeropuertos_mas_lejanos.html"


#GENERACION DEL MAPA Y DEL GRAFO
# calcular distancia (fórmula de haversine)
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2]) #conviertiendo cada posición de grados a radianes
    dlat = lat2 - lat1 #distancia en latitud
    dlon = lon2 - lon1 #distancia en longitud
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2 #aplicación de la fórmula de haversine
    c = 6371 * 2 * math.asin(math.sqrt(a)) #radio de la tierra por la raíz cuadrada de la aplicación anterior
    return c #distancia en kilometros entre los puntos

print("Cargando dataset")
df = pd.read_csv(CSV_PATH) #Lectura del dataset

print("Construyendo grafo")
G = nx.Graph() #creando grafo con la librería Network

for index, row in df.iterrows(): #recorrer cada fila
    try:
        #Asignación de cada criterio del dataset
        src = row['Source Airport Code']
        dst = row['Destination Airport Code']

        lat1 = float(row['Source Airport Latitude'])
        lon1 = float(row['Source Airport Longitude'])
        lat2 = float(row['Destination Airport Latitude'])
        lon2 = float(row['Destination Airport Longitude'])

        dist = haversine(lat1, lon1, lat2, lon2)

        # Agregar nodos al grafo
        G.add_node(src, name=row['Source Airport Name'], city=row['Source Airport City'],
                   country=row['Source Airport Country'], lat=lat1, lon=lon1)
        G.add_node(dst, name=row['Destination Airport Name'], city=row['Destination Airport City'],
                   country=row['Destination Airport Country'], lat=lat2, lon=lon2)

        # Agregar arista nueva o cambiar si existe otra con distancia menor
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
#Utilizar librería folium para crear el mapa
m = folium.Map(location=center, zoom_start=2)

# Agregar marcadores
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

#Guardar mapa (no se vuelve a tener acceso)
m.save(OUTPUT_MAP)
print(f"Mapa guardado en: {OUTPUT_MAP}")


#ACCIONES DEL PROGRAMA

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
        

#Determinar si el grafo es conexo, y si no lo es, mostrar la cantidad de componentes
def conexidad():
    lista_comp.clear() #limpiar la lista
    componentes() 
    cont = 1
    for l in lista_comp:
        #Mostrar la cantidad de componentes
        print("Componente ",cont, ": ", len(l))
        cont += 1

#Determinar el árbol de expansión mínima de cada componente del grafo
def expansion_minima():   
    lista_comp.clear() #limpiar la lista
    componentes()     
    cont = 1
    for l in lista_comp:
        v_inicial = l[0]      # el primer vértice del componente
        mst = recorrido.prim(v_inicial)
        print("Peso del árbol de expansión mínima del componente ", cont)
        print(mst)
        cont += 1

#Mostrar la información del vértice dado y de los 10 vértices más lejanos
def informacion():
    origen = input("Código del aeropuerto de origen: ").strip().upper()

    #Validación de existencia
    if origen not in G.nodes:
        print("Ese aeropuerto no existe en el grafo.")
    else:

        #Información del vértice pedido
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

    #Calcular la distancia mínima del vértice dado a los demás
        nodos, dist, pad = recorrido.dijkstra(origen)

        #Nodos pertenecientes al componente
        nodos_validos = []
        #Distancias no infinitas
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
        
        #Creación del mapa de los aeropuertos más lejanos
        origen_data = G.nodes[origen]
        mapa = folium.Map(location=[origen_data['lat'], origen_data['lon']], zoom_start=4)

        # Marcador para el aeropuerto de origen
        folium.Marker(
            location=[origen_data['lat'], origen_data['lon']],
            popup=f"<b>Origen:</b> {origen}<br>{origen_data['name']}<br>{origen_data['city']}, {origen_data['country']}",
            icon=folium.Icon(color='red', icon='circle', prefix='fa')
        ).add_to(mapa)

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
            
            # Marcador del aeropuerto
            folium.Marker(
                location=[data['lat'], data['lon']],
                popup=(f"<b>{code}</b><br>{data['name']}<br>"
                    f"{data['city']}, {data['country']}<br>"
                    f"<b>Distancia:</b> {d:.2f} km"),
                icon=folium.Icon(color='blue', icon='circle', prefix='fa')
            ).add_to(mapa)

            # Línea que une origen → aeropuerto
            folium.PolyLine(
                locations=[
                    [origen_data['lat'], origen_data['lon']],
                    [data['lat'], data['lon']]
                ],
                color='green',
                weight=2.5,
                opacity=0.8,
                tooltip=f"{origen} → {code}: {d:.2f} km"
            ).add_to(mapa)

    mapa.save("aeropuertos_mas_lejanos.html")
    webbrowser.open(f"file://{os.path.abspath(OUTPUT_AML)}")


        
def camino_minimo(G, origen, destino, camino):
    # Obtener las coordenadas promedio del camino para centrar el mapa
    lats = [G.nodes[n]['lat'] for n in camino]
    lons = [G.nodes[n]['lon'] for n in camino]
    center = (sum(lats) / len(lats), sum(lons) / len(lons))

    # Crear el mapa base
    m = folium.Map(location=center, zoom_start=4)

    # Dibujar solo los nodos del camino
    for n in camino:
        d = G.nodes[n]
        folium.CircleMarker(
            location=(d['lat'], d['lon']),
            radius=5,
            color='red',
            fill=True,
            fill_opacity=0.9,
            popup=f"{d['name']} ({n})<br>{d['city']}, {d['country']}"
        ).add_to(m)

    # Dibujar la línea del camino
    coordenadas_camino = [(G.nodes[c]['lat'], G.nodes[c]['lon']) for c in camino]
    folium.PolyLine(
        locations=coordenadas_camino,
        color='red',
        weight=3,
        opacity=0.8,
        tooltip=f"Camino mínimo: {origen} → {destino}"
    ).add_to(m)

    # Guardar y abrir el mapa
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

        #Validación de las entradas
        if vertice1 not in G.nodes and vertice2 not in G.nodes:
            print(f"Los vértices {vertice1} y {vertice2} no existen en el grafo.")
        elif vertice1 not in G.nodes:
            print(f"El vértice {vertice1} no existe en el grafo.")
        elif vertice2 not in G.nodes:
            print(f"El vértice {vertice2} no existe en el grafo.")
        else:
            nodos, dist, pad = recorrido.dijkstra(vertice1)

        # Obtener índices de los vértices en la lista de nodos
        i_destino = nodos.index(vertice2)

        #Determinar validez de la distancia
        if dist[i_destino] == float('inf'):
            print(f"->>> No existe camino entre {vertice1} y {vertice2}.")
        else:
            print(f"La distancia entre {vertice1} y {vertice2} es {dist[i_destino]:.2f} km")

            #Reconstruir el camino
            #Inicializar la lista donde estará el camino
            camino = []
            #Inicializar el vértice actual
            actual = vertice2
            while actual is not None:
                camino.insert(0, actual) #Insertar el nodo actual al inicio de la lista
                i_actual = nodos.index(actual) #Buscar el ínice del nodo actual en la lista de los vértices
                actual = pad[i_actual] #El nuevo vértice a iterar es el predecesor del actual

            print("\n>>>>>>> CAMINO MÍNIMO")
            for i, codigo in enumerate(camino): #Recorrer la lista del camino devolviendo el indice y el código
                #Obtener los datos del vértice interado
                datos = G.nodes[codigo]
                #Mostrar información detallada
                print(f"{i+1}. ({codigo}) - {datos['name']} | {datos['city']}, {datos['country']} | "
                    f"Lat: {datos['lat']:.3f}, Lon: {datos['lon']:.3f}")
            print(">>>>>>>")

            #Mostrar en el mapa
            camino_minimo(G,vertice1, vertice2, camino)                   
        
    if op == 5: 
        cont = 1
    

