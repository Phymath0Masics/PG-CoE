import matplotlib.pyplot as plt
import networkx as nx
from .model import GridModel
from typing import Dict, Tuple, List
import math
from ipywidgets import interact, IntSlider, VBox, HBox, Output, Button

def plot_grid(model: GridModel, result=None, disabled=None, defended=None, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6,5))
    G = model.G
    pos = nx.spring_layout(G, seed=42)
    flows = {}
    theta = result.get('theta') if result else None
    if theta:
        for (i,j) in G.edges():
            b = G[i][j]['b']
            flows[(i,j)] = b*(theta[i]-theta[j])
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, ax=ax)
    # draw edges individually to allow per-edge width/color without type issues
    for (i,j) in G.edges():
        if disabled and ((i,j) in disabled or (j,i) in disabled):
            color = 'red'
        elif defended and ((i,j) in defended or (j,i) in defended):
            color = 'green'
        else:
            color = 'gray'
        if flows:
            w = min(5.0, 0.05*abs(flows[(i,j)])+0.5)
        else:
            w = 1.5
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(i,j)], edge_color=color, width=w)
    if flows:
        edge_labels = {e: f"{flows[e]:.1f}" for e in flows}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    if result:
        shed_total = result.get('total_shed',0.0)
        ax.set_title(f"Total Shed: {shed_total:.2f}")
    ax.axis('off')
    return ax


def animate_attack_defense(history: List[dict], model: GridModel):
    # history: list of dicts with keys result, disabled, defended
    import matplotlib.animation as animation
    fig, ax = plt.subplots(figsize=(6,5))
    def update(frame):
        ax.clear()
        step = history[frame]
        plot_grid(model, step.get('result'), step.get('disabled'), step.get('defended'), ax=ax)
        ax.set_title(f"Step {frame+1}/{len(history)} Shed {step['result'].get('total_shed',0):.2f}")
        return []
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=1500, repeat=False)
    return ani


def interactive_attack_defense(model: GridModel, max_attack: int = 3):
    """Interactive tool to explore attacks of size k and see resulting shed."""
    out = Output()
    def view(k):
        from .opt import solve_attack_max_shed
        res = solve_attack_max_shed(model, k)
        with out:
            out.clear_output(wait=True)
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(5,4))
            plot_grid(model, res, disabled=res['disabled'], ax=ax)
            plt.show()
    interact(view, k=IntSlider(description='Attack k', min=0, max=max_attack, step=1, value=0))
    return out
