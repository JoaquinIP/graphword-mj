from typing import List
from .graph import Graph

class GraphManager:
    def __init__(self):
        self.graph_obj = Graph()

    def build_graph(self, words: List[str]):
        for i, w1 in enumerate(words):
            self.graph_obj.add_node(w1)
            for w2 in words[i+1:]:
                self.graph_obj.add_edge(w1, w2)

    def get_graph(self) -> Graph:
        return self.graph_obj

    def __repr__(self):
        return repr(self.graph_obj)
