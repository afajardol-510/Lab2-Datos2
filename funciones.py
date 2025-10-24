from collections import deque
from queue import PriorityQueue
import math

class acciones:
    def __init__(self, grafo):
        # Recibe el grafo desde otra clase
        self.grafo = grafo

    def recorridoBFS(self, raiz):
        #Recorrido por anchura
        Q = deque()
        Q.append(raiz)

        #Asignar que todos los nodos no hayan sido visitados
        visit = {v: False for v in self.grafo.nodes()}

        visit[raiz] = True #Empezar por la raiz del grafo
        vertices_comp = []

    #Mientras que la cola no esté vacía
        while Q:
            u = Q.popleft()
            vertices_comp.append(u)
            #Visitar todos los vértices adyacentes que no hayan sido visitador
            for v in self.grafo.neighbors(u):
                if not visit[v]:
                    visit[v] = True
                    Q.append(v)


        return visit, vertices_comp

    #Recorrido por anchura para las componentes
    def recorridoBFS2(self, raiz, visit):
        Q = deque()
        Q.append(raiz)
        visit[raiz] = True
        vertices_comp = []


        while Q:
            u = Q.popleft()
            vertices_comp.append(u)
            #Solo tiene en cuenta a los de la siguiente componente porque los vértices de la anterior ya fueron visitados
            for v in self.grafo.neighbors(u):
                if not visit[v]:
                    visit[v] = True
                    Q.append(v)

        return visit, vertices_comp
    
    #Arbol de expansión mínima
    def prim(self, vo):

        # Cola de prioridad para guardar las aristas (peso, vértice de origen, vertice de destino)
        q = PriorityQueue()

        # Conjuntos de vértices y aristas del árbol parcial, se inicializa con el vértice de origen
        Vt = set([vo])
        peso_total = 0
        #Aristas seleccionadas para crear el árbol
        Et = []

        # Insertar las aristas que tienen a vo
        for vi in self.grafo.neighbors(vo):
            peso = self.grafo[vo][vi].get("weight", 1)  # obtiene el peso (o 1 si no tiene)
            q.put((peso, vo, vi))  # Añadir arista a la cola provicional


        while not q.empty() and len(Vt) < self.grafo.number_of_nodes():
            peso, u, v = q.get()  # extrae la arista más ligera

            if v not in Vt:  # si el vértice aún no está en el árbol
                Vt.add(v) #Añadir la tupla de vertice y arista al conjunto del árbol parcial
                Et.append((u, v, peso))  #Añadir la arista
                peso_total += peso #Acumular el peso 

                # Insertar las nuevas aristas que salen de v
                for w in self.grafo.neighbors(v):
                    if w not in Vt:
                        w_peso = self.grafo[v][w].get("weight", 1)
                        q.put((w_peso, v, w))

        return peso_total


    #Camino mínimo
    def dijkstra(self, v):
        nodos = list(self.grafo.nodes)
        n = len(nodos)

        # Inicialización de listas
        dist = [math.inf] * n #Todas las distancias empiezan en infinito
        pad = [None] * n #Ningún vértice tiene predecesor
        visitado = [False] * n #Ningún vértice ha sido visitado

        # Validar existencia del nodo solicitado
        if v not in nodos:
            print("Ese aeropuerto no existe en el grafo.")
            return None, None, None

        #Indice del vértice en la lista de los nodos
        i_v = nodos.index(v)
        dist[i_v] = 0 #La distancia consigo mismo es 0

        # Recorremos todos los nodos
        for i in range(n):
            menor_dist = math.inf
            menor_i = -1

            for j in range(n):
                #Comprobar cuál arista tiene menor peso de las no visitadas
                if not visitado[j] and dist[j] < menor_dist:
                    menor_dist = dist[j]
                    menor_i = j

            #  Todas las aristas alcanzables ya fueron visitadas
            if menor_i == -1:
                break

            #Asignar que dicho vértice ya fue visitado
            visitado[menor_i] = True
            actual = nodos[menor_i] #Asignar el vértice actual

            # Revisar aristas del grafo para comprobar conexión con el vértice actual
            for (a, b) in self.grafo.edges:
                if a == actual or b == actual:
                    if a == actual:
                        vecino = b
                    else:
                        vecino = a

                    # Obtenemos el peso de la arista
                    peso = self.grafo[a][b]['weight']

                    j_vecino = nodos.index(vecino) #Indice del vértice conectado al vértice actual

                    #Si el vecino no ha sido visitado
                    # y la distancia formada por el nuevo peso de la arista más la menor de las no visitadas
                    # es menor que la distancia del vértice conectado:
                    if not visitado[j_vecino] and dist[menor_i] + peso < dist[j_vecino]:
                        #La distancia entre el vecino y el actual será la nueva distancia encontrada
                        dist[j_vecino] = dist[menor_i] + peso
                        #El predecesor del vecino será el vértice actual
                        pad[j_vecino] = actual

        return nodos, dist, pad   

            
    def reconstruir_camino(self, nodos, pad, origen, destino):
        #Validar que el nodo origen y destino estén en la lista de nodos
        if origen not in nodos or destino not in nodos:
            return []

        #Inicializar la lista donde estará el camino
        camino = []
        #Inicializar el actual
        actual = destino
        while actual is not None:
            camino.insert(0, actual) #Insertar el nodo actual al inicio de la lista
            i_actual = nodos.index(actual) #Buscar el ínice del nodo actual en la lista de los vértices
            actual = pad[i_actual] #El nuevo vértice a iterar es el predecesor del actual
        return camino
