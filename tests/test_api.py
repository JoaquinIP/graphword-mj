# tests/test_api.py

import os
import pytest
import requests

@pytest.fixture(scope="session")
def api_host():
    """
    Lee la variable de entorno 'API_HOST' que contendrá el DNS público
    de la instancia EC2 (ej: ec2-3-90-10-123.compute-1.amazonaws.com).
    """
    host = os.environ.get("API_HOST")
    if not host:
        pytest.fail("No se definió la variable de entorno 'API_HOST'.")
    # Asumimos que la API corre en puerto 80
    return f"http://{host}"

def test_index(api_host):
    url = f"{api_host}/"
    resp = requests.get(url)
    assert resp.status_code == 200, f"Status code inesperado: {resp.status_code}"
    data = resp.json()
    assert "Bienvenido a la API de Grafos" in data.get("message", ""), \
        "Mensaje de bienvenida no encontrado en /"

def test_shortest_path(api_host):
    url = f"{api_host}/shortest-path"
    params = {"word1": "dog", "word2": "cat"}
    resp = requests.get(url, params=params)
    # Puede ser 200 o 404 si no existe camino
    assert resp.status_code in (200, 404), f"Status code inesperado: {resp.status_code}"

def test_all_paths(api_host):
    url = f"{api_host}/all-paths"
    params = {"word1": "dog", "word2": "cat", "limit": 5}
    resp = requests.get(url, params=params)
    assert resp.status_code in (200, 404)

def test_maximum_distance_between(api_host):
    # Camino más largo entre dog y cat, limit=7
    url = f"{api_host}/maximum-distance"
    params = {"word1": "dog", "word2": "cat", "limit": 7}
    resp = requests.get(url, params=params)
    assert resp.status_code == 200 or resp.status_code == 404

def test_maximum_distance_global(api_host):
    # Si no paso word1, word2 => camino más largo global
    url = f"{api_host}/maximum-distance"
    resp = requests.get(url)
    assert resp.status_code == 200

def test_clusters(api_host):
    url = f"{api_host}/clusters"
    resp = requests.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert "clusters" in data

def test_high_connectivity(api_host):
    url = f"{api_host}/high-connectivity"
    params = {"degree": 2}
    resp = requests.get(url, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data

def test_nodes_by_degree(api_host):
    url = f"{api_host}/nodes-by-degree"
    params = {"degree": 3}
    resp = requests.get(url, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data

def test_isolated_nodes(api_host):
    url = f"{api_host}/isolated-nodes"
    resp = requests.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert "isolated_nodes" in data
