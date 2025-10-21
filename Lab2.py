"""
- Carga el dataset flights_final.csv
- Construye un grafo no dirigido y ponderado (NetworkX) donde los vértices
  son aeropuertos (clave: Airport Code) y las aristas tienen peso = distancia (km)
  calculada por la fórmula haversine usando lat/lon.
- Guarda un mapa interactivo (HTML) con la geolocalización de los aeropuertos
  y traza el árbol de expansión mínima (MST) de cada componente para evitar
  dibujar miles de aristas.

    pip install pandas networkx folium

Notas:
- El script asume que el CSV tiene columnas con exactamente los nombres descritos
  en la consigna (Source Airport Code, Source Airport Latitude, etc.).
- Si el CSV tiene nombres distintos o separador diferente, editar la variable
  `CSV_PARAMS` abajo.
"""

import argparse
import math
from collections import defaultdict
import pandas as pd
import networkx as nx
import folium

# ------------------ Config / CSV reading params ------------------
CSV_PARAMS = {
    'filepath_or_buffer': None,  # se asigna por args
    'sep': ',',
    'quotechar': '"',
}

# nombres de columnas esperadas (ajustar si el CSV difiere)
C_SRC_CODE = 'Source Airport Code'
C_SRC_NAME = 'Source Airport Name'
C_SRC_CITY = 'Source Airport City'
C_SRC_COUNTRY = 'Source Airport Country'
C_SRC_LAT = 'Source Airport Latitude'
C_SRC_LON = 'Source Airport Longitude'
C_DST_CODE = 'Destination Airport Code'
C_DST_NAME = 'Destination Airport Name'
C_DST_CITY = 'Destination Airport City'
C_DST_COUNTRY = 'Destination Airport Country'
C_DST_LAT = 'Destination Airport Latitude'
C_DST_LON = 'Destination Airport Longitude'

# ------------------ Utilities ------------------

def haversine(lat1, lon1, lat2, lon2):
    """Return distance between two points in kilometers using haversine."""
    # convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0088  # Earth radius in km (mean)
    return R * c

# ------------------ Graph building ------------------

def build_graph_from_df(df):
    """Construye y retorna un NetworkX Graph a partir del dataframe.
    Nodos: códigos de aeropuerto con atributos: name, city, country, lat, lon
    Aristas: peso = distancia en km (haversine). Si hay múltiples registros
    entre los mismos dos aeropuertos, se conserva la arista con menor peso.
    """
    G = nx.Graph()

    # Agregar nodos: extraer de source y destination
    nodes = {}
    for prefix in ['Source', 'Destination']:
        code_col = f'{prefix} Airport Code'
        name_col = f'{prefix} Airport Name'
        city_col = f'{prefix} Airport City'
        country_col = f'{prefix} Airport Country'
        lat_col = f'{prefix} Airport Latitude'
        lon_col = f'{prefix} Airport Longitude'

        for _, row in df[[code_col, name_col, city_col, country_col, lat_col, lon_col]].drop_duplicates().iterrows():
            code = row[code_col]
            if pd.isna(code):
                continue
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])
            except Exception:
                # saltar si coordenadas inválidas
                continue
            if code not in nodes:
                nodes[code] = {
                    'code': code,
                    'name': row[name_col] if pd.notna(row[name_col]) else '',
                    'city': row[city_col] if pd.notna(row[city_col]) else '',
                    'country': row[country_col] if pd.notna(row[country_col]) else '',
                    'lat': lat,
                    'lon': lon,
                }
    # Añadir nodos al grafo
    for code, attr in nodes.items():
        G.add_node(code, **attr)

    # Construir aristas: usar un dict para conservar la arista con menor distancia
    edge_min = {}
    for _, row in df[[C_SRC_CODE, C_SRC_LAT, C_SRC_LON, C_DST_CODE, C_DST_LAT, C_DST_LON]].iterrows():
        a = row[C_SRC_CODE]
        b = row[C_DST_CODE]
        if pd.isna(a) or pd.isna(b):
            continue
        if a == b:
            continue
        try:
            lat1 = float(row[C_SRC_LAT]); lon1 = float(row[C_SRC_LON])
            lat2 = float(row[C_DST_LAT]); lon2 = float(row[C_DST_LON])
        except Exception:
            continue
        # calcular distancia
        dist = haversine(lat1, lon1, lat2, lon2)
        key = tuple(sorted([a, b]))
        if key not in edge_min or dist < edge_min[key]['weight']:
            edge_min[key] = {'u': key[0], 'v': key[1], 'weight': dist}

    # Añadir aristas al grafo
    for key, e in edge_min.items():
        if e['u'] in G.nodes and e['v'] in G.nodes:
            G.add_edge(e['u'], e['v'], weight=e['weight'])

    return G

# ------------------ Map saving ------------------

def save_map_with_nodes_and_mst(G, out_html_path):
    """Crea un mapa folium con marcadores para cada aeropuerto y traza las aristas
    del árbol de expansión mínima por componente (para no sobrecargar el mapa).
    Guarda el mapa en out_html_path.
    """
    if len(G.nodes) == 0:
        raise ValueError('El grafo está vacío. No hay nodos para mapear.')

    # centro aproximado
    lats = [G.nodes[n]['lat'] for n in G.nodes]
    lons = [G.nodes[n]['lon'] for n in G.nodes]
    center = (sum(lats) / len(lats), sum(lons) / len(lons))

    m = folium.Map(location=center, zoom_start=2)

    # agregar marcadores (popup con info)
    for n, d in G.nodes(data=True):
        popup = (f"<b>{d.get('code','')}</b><br>" +
                 f"{d.get('name','')}<br>{d.get('city','')}, {d.get('country','')}<br>" +
                 f"Lat: {d.get('lat'):.6f}, Lon: {d.get('lon'):.6f}")
        folium.CircleMarker(location=(d['lat'], d['lon']), radius=3, popup=popup, fill=True).add_to(m)

    # dibujar MST por componente (menos aristas y significativo)
    for component in nx.connected_components(G):
        sub = G.subgraph(component).copy()
        if sub.number_of_edges() == 0:
            continue
        mst = nx.minimum_spanning_tree(sub, weight='weight')
        # trazamos cada arista del MST
        for u, v, data in mst.edges(data=True):
            uattr = G.nodes[u]; vattr = G.nodes[v]
            folium.PolyLine(locations=[(uattr['lat'], uattr['lon']), (vattr['lat'], vattr['lon'])], weight=1).add_to(m)

    m.save(out_html_path)
    print(f'Mapa guardado en: {out_html_path}')

# ------------------ CLI / main ------------------

def main():
    parser = argparse.ArgumentParser(description='Construir grafo de aeropuertos desde CSV y generar mapa HTML')
    parser.add_argument('--csv', required=True, help='Ruta al archivo flights_final.csv')
    parser.add_argument('--outmap', default='airports_map.html', help='Archivo HTML de salida para el mapa')
    parser.add_argument('--print-summary', action='store_true', help='Imprime resumen: número de nodos, aristas y componentes')
    args = parser.parse_args()

    CSV_PARAMS['filepath_or_buffer'] = args.csv
    print('Cargando CSV...')
    df = pd.read_csv(**CSV_PARAMS)
    print('CSV cargado: filas =', len(df))

    print('Construyendo grafo... (esto puede tardar unos segundos)')
    G = build_graph_from_df(df)
    print('Grafo construido: nodos =', G.number_of_nodes(), 'aristas =', G.number_of_edges())

    if args.print_summary:
        comps = list(nx.connected_components(G))
        print('Componentes conectados =', len(comps))
        for i, comp in enumerate(comps, 1):
            print(f'  Componente {i}: vértices = {len(comp)}')

    print('Generando mapa (dibujando MST por componente para evitar sobrecarga)...')
    save_map_with_nodes_and_mst(G, args.outmap)

    print('\nHecho. Sugerencias siguientes:')
    print(' - Abrir el HTML generado en el navegador para explorar los aeropuertos.')
    print(' - A partir de aquí puedes implementar funciones interactivas:')
    print('   * Determinar si el grafo es conexo (nx.is_connected)')
    print('   * MST y su peso (nx.minimum_spanning_tree + sum(edge weights))')
    print('   * Dijkstra desde un código (nx.single_source_dijkstra_path_length)')
    print('   * Camino mínimo entre dos códigos (nx.dijkstra_path) y trazarlo en el mapa')

if __name__ == '__main__':
    main()
