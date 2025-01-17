import os
import pytest
import requests

@pytest.fixture(scope="session")
def api_host():
    host = os.environ.get("API_HOST")
    if not host:
        pytest.fail("Environment variable 'API_HOST' was not defined.")
    return f"http://{host}"

def test_index(api_host):
    url = f"{api_host}/"
    resp = requests.get(url)
    assert resp.status_code == 200, f"Status code unexpected: {resp.status_code}"
    data = resp.json()
    assert "Welcome to the Graph API" in data.get("message", ""), \
        "Welcome message not found in /"

def test_shortest_path(api_host):
    url = f"{api_host}/shortest-path"
    params = {"word1": "dog", "word2": "cat"}
    resp = requests.get(url, params=params)
    assert resp.status_code in (200, 404), f"Status code unexpected: {resp.status_code}"

def test_all_paths(api_host):
    url = f"{api_host}/all-paths"
    params = {"word1": "dog", "word2": "cat", "limit": 5}
    resp = requests.get(url, params=params)
    assert resp.status_code in (200, 404)

def test_maximum_distance_between(api_host):
    url = f"{api_host}/maximum-distance"
    params = {"word1": "dog", "word2": "cat", "limit": 7}
    resp = requests.get(url, params=params)
    assert resp.status_code == 200 or resp.status_code == 404

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
