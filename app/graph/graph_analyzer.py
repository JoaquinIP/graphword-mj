# graph/graph_analyzer.py

import networkx as nx
from typing import Optional, List
import matplotlib.pyplot as plt
from graph.node import Node

class GraphAnalyzer:
    """
    Encapsula la lógica de análisis de un grafo de palabras:
      - Info básica: número de nodos, aristas, grado medio...
      - Caminos más cortos
      - Todos los caminos
      - Distancia máxima
      - Clústeres
      - Nodos de alta conectividad
      - Selección de nodos por grado
      - Nodos aislados
    """

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def get_basic_info(self) -> dict:
        n = self.graph.number_of_nodes()
        degree_sum = sum(dict(self.graph.degree()).values())
        connected_components = list(nx.connected_components(self.graph))

        info = {
            'number_of_nodes': n,
            'number_of_edges': self.graph.number_of_edges(),
            'average_degree': degree_sum / n if n > 0 else 0,
            'number_of_connected_components': len(connected_components),
            'largest_component_size': max(len(c) for c in connected_components) if connected_components else 0
        }
        return info

    def get_degree_distribution(self) -> dict:
        distribution = {}
        for _, deg in self.graph.degree():
            distribution[deg] = distribution.get(deg, 0) + 1
        return distribution
    
    def maximum_distance_among_all(self, limit: Optional[int] = None) -> (int, List[str]):
        """
        Retorna (dist, path) donde 'dist' es el número de aristas del
        camino simple más largo en TODO el grafo, y 'path' es la secuencia
        de palabras (str) de ese camino. Si limit != None, no buscará
        caminos con más de 'limit' aristas.
        """
        best_dist = 0
        best_path_nodes = []

        nodes_list = list(self.graph.nodes)
        n = len(nodes_list)

        for i in range(n):
            for j in range(i + 1, n):
                start_node = nodes_list[i]
                end_node = nodes_list[j]
                cutoff_val = limit if limit is not None else None

                # Enumeramos todas las rutas simples entre start_node y end_node
                for path_nodes in nx.all_simple_paths(
                        self.graph, start_node, end_node, cutoff=cutoff_val):
                    dist = len(path_nodes) - 1  # número de aristas
                    if dist > best_dist:
                        best_dist = dist
                        best_path_nodes = path_nodes

        best_path_str = [n.word for n in best_path_nodes]
        return best_dist, best_path_str

    def maximum_distance_between(self, source: str, target: str, limit: Optional[int] = None) -> (int, List[str]):
        """
        Retorna (dist, path) del camino simple más largo entre 'source' y 'target' (strings),
        sin ciclos y con longitud en aristas <= limit (si se define).

        Si no hay caminos, dist=0 y path=[].
        """
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            # No existen esos nodos en el grafo
            return 0, []

        best_dist = 0
        best_path_nodes = []
        cutoff_val = limit if limit is not None else None

        # Explora todas las rutas simples entre s_node y t_node
        for path_nodes in nx.all_simple_paths(self.graph, s_node, t_node, cutoff=cutoff_val):
            dist = len(path_nodes) - 1
            if dist > best_dist:
                best_dist = dist
                best_path_nodes = path_nodes

        best_path_str = [n.word for n in best_path_nodes]
        return best_dist, best_path_str

    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Retorna la lista de nodos (strings) que conforman el camino más corto entre 'source' y 'target'.
        Si no existe camino, retorna None.
        """
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            return None

        try:
            path_nodes = nx.shortest_path(self.graph, source=s_node, target=t_node)
            # Convertir cada Node(...) a su string .word
            return [n.word for n in path_nodes]
        except nx.NetworkXNoPath:
            return None

    def all_paths(self, source: str, target: str, limit: int = 10) -> List[List[str]]:
        """
        Retorna todas las rutas simples entre source y target (limitado a 'limit').
        Cada ruta se representa como lista de strings.
        """
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            return []

        paths_generator = nx.all_simple_paths(self.graph, s_node, t_node)
        paths_list = []
        for i, p in enumerate(paths_generator):
            if i >= limit:
                break
            # Convertimos cada ruta de Node(...) a strings
            path_str = [node.word for node in p]
            paths_list.append(path_str)
        return paths_list

    def maximum_distance(self) -> int:
        """
        Distancia máxima entre cualquier par de nodos del grafo.
        (El valor de la ruta más larga sin ciclos.)
        """
        max_dist = 0
        # Cada 'node' es un Node(...) dentro de self.graph
        for node in self.graph.nodes:
            lengths = nx.single_source_shortest_path_length(self.graph, node)
            max_node_dist = max(lengths.values(), default=0)
            max_dist = max(max_dist, max_node_dist)
        return max_dist

    def clusters(self):
        """
        Retorna una lista de componentes conexas (clusters),
        cada componente es un set de Node(...).
        """
        return list(nx.connected_components(self.graph))

    def high_connectivity_nodes(self, threshold: int = 1) -> List[str]:
        """
        Retorna los nodos (strings) con un grado >= threshold.
        """
        result = []
        for n, d in self.graph.degree():
            if d >= threshold:
                # n es Node(...), convertimos a n.word
                result.append(n.word)
        return result

    def nodes_by_degree(self, degree: int) -> List[str]:
        """
        Retorna los nodos (strings) con un grado == degree.
        """
        result = []
        for n, d in self.graph.degree():
            if d == degree:
                result.append(n.word)
        return result

    def isolated_nodes(self) -> List[str]:
        """
        Retorna lista de nodos (strings) sin aristas (aislados).
        """
        return [n.word for n in nx.isolates(self.graph)]

    def visualize_graph(self, show_labels: bool = True):
        """
        Dibuja el grafo usando matplotlib. 
        """
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)

        nx.draw_networkx_nodes(self.graph, pos,
                               node_color='lightblue',
                               node_size=500,
                               alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray')

        if show_labels:
            # n es Node(...), convertir n.word
            labels = {n: n.word for n in self.graph.nodes}
            nx.draw_networkx_labels(self.graph, pos, labels=labels,
                                    font_size=10, font_color='black')

        plt.axis('off')
        plt.title("Visualización del Grafo")
        plt.show()
