import networkx as nx
from typing import Optional, List
import matplotlib.pyplot as plt
from graph.node import Node

class GraphAnalyzer:
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
    
    def maximum_distance_among_all(self, limit: Optional[int] = None) -> (int, List[str]): # type: ignore
        best_dist = 0
        best_path_nodes = []

        nodes_list = list(self.graph.nodes)
        n = len(nodes_list)

        for i in range(n):
            for j in range(i + 1, n):
                start_node = nodes_list[i]
                end_node = nodes_list[j]
                cutoff_val = limit if limit is not None else None

                for path_nodes in nx.all_simple_paths(
                        self.graph, start_node, end_node, cutoff=cutoff_val):
                    dist = len(path_nodes) - 1
                    if dist > best_dist:
                        best_dist = dist
                        best_path_nodes = path_nodes

        best_path_str = [n.word for n in best_path_nodes]
        return best_dist, best_path_str

    def maximum_distance_between(self, source: str, target: str, limit: Optional[int] = None) -> (int, List[str]): # type: ignore
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            return 0, []

        best_dist = 0
        best_path_nodes = []
        cutoff_val = limit if limit is not None else None

        for path_nodes in nx.all_simple_paths(self.graph, s_node, t_node, cutoff=cutoff_val):
            dist = len(path_nodes) - 1
            if dist > best_dist:
                best_dist = dist
                best_path_nodes = path_nodes

        best_path_str = [n.word for n in best_path_nodes]
        return best_dist, best_path_str

    def shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            return None

        try:
            path_nodes = nx.shortest_path(self.graph, source=s_node, target=t_node)
            return [n.word for n in path_nodes]
        except nx.NetworkXNoPath:
            return None

    def all_paths(self, source: str, target: str, limit: int = 10) -> List[List[str]]:
        s_node = Node(source)
        t_node = Node(target)

        if s_node not in self.graph or t_node not in self.graph:
            return []

        paths_generator = nx.all_simple_paths(self.graph, s_node, t_node)
        paths_list = []
        for i, p in enumerate(paths_generator):
            if i >= limit:
                break
            path_str = [node.word for node in p]
            paths_list.append(path_str)
        return paths_list

    def maximum_distance(self) -> int:
        max_dist = 0
        for node in self.graph.nodes:
            lengths = nx.single_source_shortest_path_length(self.graph, node)
            max_node_dist = max(lengths.values(), default=0)
            max_dist = max(max_dist, max_node_dist)
        return max_dist

    def clusters(self):
        return list(nx.connected_components(self.graph))

    def high_connectivity_nodes(self, threshold: int = 1) -> List[str]:
        result = []
        for n, d in self.graph.degree():
            if d >= threshold:
                result.append(n.word)
        return result

    def nodes_by_degree(self, degree: int) -> List[str]:
        result = []
        for n, d in self.graph.degree():
            if d == degree:
                result.append(n.word)
        return result

    def isolated_nodes(self) -> List[str]:
        return [n.word for n in nx.isolates(self.graph)]

    def visualize_graph(self, show_labels: bool = True):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)

        nx.draw_networkx_nodes(self.graph, pos,
                               node_color='lightblue',
                               node_size=500,
                               alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray')

        if show_labels:
            labels = {n: n.word for n in self.graph.nodes}
            nx.draw_networkx_labels(self.graph, pos, labels=labels,
                                    font_size=10, font_color='black')

        plt.axis('off')
        plt.title("Graph Visualization")
        plt.show()
