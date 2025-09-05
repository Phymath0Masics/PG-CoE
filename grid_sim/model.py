import networkx as nx
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional

@dataclass
class GridModel:
    G: nx.Graph
    theta_min: float
    theta_max: float
    g_min: Dict[int, float]
    g_max: Dict[int, float]
    c_min: Dict[int, float]
    c_max: Dict[int, float]
    baseMVA: float = 100.0
    susceptance: Dict[Tuple[int,int], float] = field(default_factory=dict)
    demand: Dict[int, float] = field(default_factory=dict)  # positive load demand at node
    gen_cost: Dict[int, float] = field(default_factory=dict)  # linear cost for gen (optional)
    capacitance: Dict[Tuple[int,int], float] = field(default_factory=dict)

    def copy(self):
        return GridModel(self.G.copy(), self.theta_min, self.theta_max,
                         dict(self.g_min), dict(self.g_max), dict(self.c_min), dict(self.c_max),
                         self.baseMVA, dict(self.susceptance), dict(self.demand), dict(self.gen_cost),
                         dict(self.capacitance))

    @property
    def buses(self):
        return list(self.G.nodes())

    @property
    def lines(self):
        return list(self.G.edges())

    def add_line(self, i, j, b: float, capacity: float):
        self.G.add_edge(i, j, b=b, capacity=capacity)
        self.susceptance[(i,j)] = b
        self.susceptance[(j,i)] = b

    def set_demand(self, bus: int, p: float):
        self.demand[bus] = p

    def set_generator(self, bus: int, gmin: float, gmax: float, cost: float = 0.0):
        self.g_min[bus] = gmin
        self.g_max[bus] = gmax
        self.gen_cost[bus] = cost

    def set_controllable_load(self, bus: int, cmin: float, cmax: float):
        self.c_min[bus] = cmin
        self.c_max[bus] = cmax

    def export_data(self):
        return {
            'buses': self.buses,
            'lines': [(i,j, self.G[i][j]['b'], self.G[i][j]['capacity']) for i,j in self.lines],
            'g_min': self.g_min,
            'g_max': self.g_max,
            'c_min': self.c_min,
            'c_max': self.c_max,
            'demand': self.demand
        }
