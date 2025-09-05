import networkx as nx
import numpy as np
from .model import GridModel
from typing import Tuple

def random_grid(n_buses: int = 10, density: float = 0.3, seed: int = 0) -> GridModel:
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    G.add_nodes_from(range(n_buses))
    # random geometric or Erdos-Renyi
    for i in range(n_buses):
        for j in range(i+1, n_buses):
            if rng.random() < density:
                b = rng.uniform(5, 20)  # susceptance
                cap = rng.uniform(50, 200)
                G.add_edge(i, j, b=b, capacity=cap)
    # ensure connectivity (simple chain if disconnected)
    if not nx.is_connected(G):
        nodes = list(G.nodes())
        for i in range(len(nodes)-1):
            if not G.has_edge(nodes[i], nodes[i+1]):
                b = rng.uniform(5, 20)
                cap = rng.uniform(50, 200)
                G.add_edge(nodes[i], nodes[i+1], b=b, capacity=cap)
    g_min = {}
    g_max = {}
    c_min = {}
    c_max = {}
    demand = {}
    gen_cost = {}
    # assign some generators and loads
    for bus in G.nodes():
        load = rng.uniform(10, 80)
        demand[bus] = load
        c_min[bus] = 0.0
        c_max[bus] = load  # can shed all of it if needed
        if rng.random() < 0.3:  # generator
            g_min[bus] = 0.0
            g_max[bus] = rng.uniform(50, 150)
            gen_cost[bus] = rng.uniform(5, 40)
    # at least one generator
    if not g_max:
        bus = rng.integers(0, n_buses)
        g_min[bus] = 0.0
        g_max[bus] = 150.0
        gen_cost[bus] = 10.0
    model = GridModel(G, -np.pi/4, np.pi/4, g_min, g_max, c_min, c_max)
    model.demand = demand
    model.gen_cost = gen_cost
    # store susceptance dictionary
    for i,j in G.edges():
        model.susceptance[(i,j)] = G[i][j]['b']
        model.susceptance[(j,i)] = G[i][j]['b']
    # store capacitance dictionary
    for i,j in G.edges():
        model.capacitance[(i,j)] = G[i][j]['capacity']
        model.capacitance[(j,i)] = G[i][j]['capacity']
    return model
