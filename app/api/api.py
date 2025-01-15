# api/api.py

from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import sys
import pickle
import networkx as nx
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_MART_PATH
from graph.graph import Graph
from graph.graph_analyzer import GraphAnalyzer

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

graph = Graph()
analyzer = None
is_initialized = False

def load_graph():
    global is_initialized, analyzer
    try:
        serialized_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'graph.pkl'
        )
        if not os.path.isfile(serialized_path):
            logger.error(f"Archivo serializado del grafo no encontrado en {serialized_path}")
            return False

        with open(serialized_path, 'rb') as f:
            graph.graph = pickle.load(f)
        analyzer = GraphAnalyzer(graph.graph)

        is_initialized = True
        logger.info(f"Grafo cargado desde {serialized_path}: "
                    f"{graph.graph.number_of_nodes()} nodos, {graph.graph.number_of_edges()} aristas.")
        return True
    except Exception as e:
        logger.error(f"Error al cargar el grafo serializado: {e}", exc_info=True)
        return False

if load_graph():
    logger.info("La aplicación ha iniciado con el grafo ya cargado.")
else:
    logger.error("La aplicación ha iniciado sin un grafo cargado.")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Bienvenido a la API de Grafos",
        "endpoints": {
            "GET /shortest-path?word1=...&word2=...": "Camino más corto entre dos palabras",
            "GET /all-paths?word1=...&word2=...&limit=10": "Todas las rutas posibles entre dos palabras",
            "GET /maximum-distance(?word1=..&word2=..&limit=..)": 
                "Camino más largo global o entre dos nodos, con cutoff opcional",
            "GET /clusters": "Componentes conectados",
            "GET /high-connectivity?degree=2": "Nodos con grado >= 2",
            "GET /nodes-by-degree?degree=n": "Nodos con grado == n",
            "GET /isolated-nodes": "Nodos aislados"
        }
    })

@app.route("/shortest-path", methods=["GET"])
def get_shortest_path():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado correctamente."}), 500
    w1 = request.args.get("word1")
    w2 = request.args.get("word2")
    if not w1 or not w2:
        return jsonify({"error": "Faltan parámetros: word1 y word2."}), 400

    try:
        path = analyzer.shortest_path(w1, w2)
        if path is None:
            return jsonify({"message": f"No se encontró un camino entre '{w1}' y '{w2}'."}), 404
        return jsonify({"path": path})
    except Exception as e:
        logger.error(f"Error en /shortest-path: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/all-paths", methods=["GET"])
def get_all_paths():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado correctamente."}), 500
    w1 = request.args.get("word1")
    w2 = request.args.get("word2")
    limit = request.args.get("limit", default=10, type=int)
    if not w1 or not w2:
        return jsonify({"error": "Faltan parámetros: word1 y word2."}), 400

    try:
        paths = analyzer.all_paths(w1, w2, limit)
        return jsonify({"all_paths": paths})
    except Exception as e:
        logger.error(f"Error en /all-paths: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/maximum-distance", methods=["GET"])
def get_maximum_distance():
    """
    Si se proveen word1 y word2 => retorna el camino más largo (simple) entre esos nodos,
    con cutoff en 'limit' aristas (opcional).
    De lo contrario, busca en TODO el grafo el camino más largo (entre cualquier par), 
    también con cutoff si 'limit' se define.
    """
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado."}), 500

    word1 = request.args.get("word1")  # opcional
    word2 = request.args.get("word2")  # opcional
    limit = request.args.get("limit", type=int)  # None si no se pasa

    try:
        if word1 and word2:
            # Camino más largo entre word1 y word2
            dist, path = analyzer.maximum_distance_between(word1, word2, limit)
            return jsonify({
                "distance": dist,
                "path": path,
                "note": f"Camino más largo entre '{word1}' y '{word2}' con cutoff={limit}"
            })
        else:
            # Camino más largo global
            dist, path = analyzer.maximum_distance_among_all(limit)
            return jsonify({
                "distance": dist,
                "path": path,
                "note": f"Camino más largo en TODO el grafo, cutoff={limit}"
            })
    except Exception as e:
        logger.error(f"Error en /maximum-distance: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/clusters", methods=["GET"])
def get_clusters():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado correctamente."}), 500
    try:
        clusters = analyzer.clusters()
        cluster_list = []
        for c in clusters:
            cluster_list.append([node.word for node in c])
        return jsonify({"clusters": cluster_list})
    except Exception as e:
        logger.error(f"Error en /clusters: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/high-connectivity", methods=["GET"])
def get_high_connectivity():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado."}), 500
    degree = request.args.get("degree", default=2, type=int)
    try:
        nodes = analyzer.high_connectivity_nodes(degree)
        return jsonify({"nodes": nodes})
    except Exception as e:
        logger.error(f"Error en /high-connectivity: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/nodes-by-degree", methods=["GET"])
def get_nodes_by_degree():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado."}), 500
    deg = request.args.get("degree", type=int)
    if deg is None:
        return jsonify({"error": "Falta parámetro: degree."}), 400
    try:
        nodes = analyzer.nodes_by_degree(deg)
        return jsonify({"nodes": nodes})
    except Exception as e:
        logger.error(f"Error en /nodes-by-degree: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/isolated-nodes", methods=["GET"])
def get_isolated_nodes():
    if not is_initialized:
        return jsonify({"error": "Grafo no inicializado."}), 500
    try:
        isolated = analyzer.isolated_nodes()
        return jsonify({"isolated_nodes": isolated})
    except Exception as e:
        logger.error(f"Error en /isolated-nodes: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/routes", methods=["GET"])
def list_routes():
    import urllib
    output = {}
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(str(rule))
        output[url] = methods
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
