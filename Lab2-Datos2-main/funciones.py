from collections import deque
from queue import PriorityQueue
import math

class acciones:
    def __init__(self, grafo):
        # Recibe el grafo desde otra clase
        self.grafo = grafo

    def recorridoBFS(self, raiz):
        """Realiza la búsqueda en anchura (BFS) desde el nodo s."""
        Q = deque()
        Q.append(raiz)

        visit = {v: False for v in self.grafo.nodes()}

        visit[raiz] = True
        vertices_comp = []

        #print(f"Recorrido BFS desde {raiz}:")
        while Q:
            u = Q.popleft()
            vertices_comp.append(u)

            for v in self.grafo.neighbors(u):
                if not visit[v]:
                    visit[v] = True
                    Q.append(v)


        return visit, vertices_comp

    def recorridoBFS2(self, raiz, visit):
        Q = deque()
        Q.append(raiz)
        visit[raiz] = True
        vertices_comp = []

        #print(f"Recorrido BFS desde {raiz}:")
        while Q:
            u = Q.popleft()
            vertices_comp.append(u)

            for v in self.grafo.neighbors(u):
                if not visit[v]:
                    visit[v] = True
                    Q.append(v)

        return visit, vertices_comp
    
    def prim(self, vo):
        """Aplica el algoritmo de Prim desde el vértice vo."""

        # Cola de prioridad para guardar las aristas (peso, origen, destino)
        q = PriorityQueue()

        # Conjuntos de vértices y aristas del árbol parcial
        Vt = set([vo])
        peso_total = 0
        Et = []

        # Insertar las aristas del vértice inicial
        for vi in self.grafo.neighbors(vo):
            peso = self.grafo[vo][vi].get("weight", 1)  # obtiene el peso (o 1 si no tiene)
            q.put((peso, vo, vi))  # (prioridad, origen, destino)

        # Bucle principal
        while not q.empty() and len(Vt) < self.grafo.number_of_nodes():
            peso, u, v = q.get()  # extrae la arista más ligera

            if v not in Vt:  # si el vértice aún no está en el árbol
                Vt.add(v)
                Et.append((u, v, peso))  # añade la arista al MST
                peso_total += peso

                # insertar las nuevas aristas que salen de v
                for w in self.grafo.neighbors(v):
                    if w not in Vt:
                        w_peso = self.grafo[v][w].get("weight", 1)
                        q.put((w_peso, v, w))

        return peso_total

    def dijkstra(self, v):
        nodos = list(self.grafo.nodes)
        n = len(nodos)

        # Inicialización de listas
        dist = [math.inf] * n
        pad = [None] * n
        visitado = [False] * n

        # Buscar índice del nodo de origen
        if v not in nodos:
            print("Ese aeropuerto no existe en el grafo.")
            return None, None, None

        i_v = nodos.index(v)
        dist[i_v] = 0

        # Recorremos todos los nodos
        for i in range(n):
            # Buscar el nodo no visitado con menor distancia
            menor_dist = math.inf
            menor_i = -1

            for j in range(n):
                if not visitado[j] and dist[j] < menor_dist:
                    menor_dist = dist[j]
                    menor_i = j

            if menor_i == -1:
                break

            visitado[menor_i] = True
            actual = nodos[menor_i]

            # Revisar conexiones del nodo actual
            for (a, b) in self.grafo.edges:
                if a == actual or b == actual:
                    if a == actual:
                        vecino = b
                    else:
                        vecino = a

                    # Obtenemos el peso de la arista
                    peso = self.grafo[a][b]['weight']

                    j_vecino = nodos.index(vecino)

                    if not visitado[j_vecino] and dist[menor_i] + peso < dist[j_vecino]:
                        dist[j_vecino] = dist[menor_i] + peso
                        pad[j_vecino] = actual

        return nodos, dist, pad   

    def reconstruir_camino(self, prev, origen, destino):
            camino = []               # Lista para guardar los nodos del camino
            actual = destino           # Comienza desde el nodo destino

            # Retrocede desde el destino hasta el origen usando los predecesores
            while actual is not None:
                camino.insert(0, actual)   # Inserta al inicio de la lista (construye el camino de atrás hacia adelante)
                actual = prev[actual]      # Avanza hacia el nodo previo

            # Verifica si el camino reconstruido empieza realmente en el origen
            if camino[0] == origen:
                return camino              # Devuelve el camino encontrado
            else:
                return []                  # Si no, devuelve una lista vacía (no hay conexión)