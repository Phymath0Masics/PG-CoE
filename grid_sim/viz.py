import matplotlib.pyplot as plt
import networkx as nx
from .model import GridModel
from typing import Dict, Tuple, List, Optional
import math
from ipywidgets import interact, IntSlider, VBox, HBox, Output, Button
from matplotlib.patches import FancyArrowPatch, Patch
from matplotlib.lines import Line2D
from matplotlib import colors as mcolors

def plot_grid(
    model: GridModel,
    result: Optional[dict] = None,
    disabled=None,
    defended=None,
    ax=None,
    layout: Optional[Dict[int, Tuple[float,float]]] = None,
    show_edge_labels: bool = False,
    cmap: str = 'Reds',
    scale_arrows: float = 0.12,
    node_size_base: int = 600,
    annotate: bool = True
):
    """Visualize the grid with detailed annotations.

    Features added:
    - Node color intensity = shedding (absolute) with colorbar
    - Multi-line node labels (bus id, gen, demand, shed)
    - Directed flow arrows with width scaled by |flow|
    - Edge coloring: red (disabled), green (defended), gray (normal)
    - Optional flow magnitude labels
    - Legends for line status and arrow scale reference
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7,6))
    G = model.G
    if layout is not None:
        pos = layout
    else:
        # deterministic spring layout for stability
        pos = nx.spring_layout(G, seed=42)

    # Extract solution pieces
    theta = result.get('theta') if result else None
    g = result.get('g') if result else {}
    shed = result.get('shed') if result else {}
    demand = model.demand

    # Compute flows (directional)
    flows = {}
    if theta:
        for (i, j) in G.edges():
            b = G[i][j]['b']
            f = b * (theta[i] - theta[j])
            flows[(i, j)] = f

    # Node shedding values for color mapping
    nodes_list = list(G.nodes())
    shed_dict = shed if isinstance(shed, dict) else {}
    shed_vals = [shed_dict.get(n, 0.0) for n in nodes_list]
    max_shed = max(shed_vals) if shed_vals else 0.0
    if max_shed <= 0:
        # fallback: uniform color if no shedding
        node_colors = ['#c6dbef'] * len(nodes_list)
        norm = None
    else:
        norm = mcolors.Normalize(vmin=0, vmax=max_shed)
        cmap_obj = plt.cm.get_cmap(cmap)
        node_colors = [cmap_obj(norm(s)) for s in shed_vals]

    # Scale node size by demand (optional) and shedding highlight ring
    node_sizes = []
    for n in nodes_list:
        base = node_size_base
        d = demand.get(n, 0.0)
        node_sizes.append(base * (0.4 + 0.6 * (d / (max(demand.values()) if demand else 1))))

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, edgecolors='black', linewidths=0.8)

    # Node labels
    if annotate:
        node_labels = {}
        for n in nodes_list:
            lab = f"{n}"
            if g:
                lab += f"\nG:{g.get(n,0):.1f}"
            if demand:
                lab += f" D:{demand.get(n,0):.1f}"
            if shed:
                val_s = shed.get(n,0.0)
                if val_s > 1e-6:
                    lab += f"\nS:{val_s:.1f}"
            node_labels[n] = lab
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, ax=ax)

    # Draw edges with directional arrows
    max_flow_abs = max((abs(f) for f in flows.values()), default=0.0)
    for (i, j) in G.edges():
        # Choose representative flow direction
        f = flows.get((i, j))
        # edge status color
        if disabled and ((i, j) in disabled or (j, i) in disabled):
            color = 'red'
        elif defended and ((i, j) in defended or (j, i) in defended):
            color = 'green'
        else:
            color = 'gray'
        if f is None:
            # no solution yet: draw undirected thin line
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(i, j)], edge_color=color, width=1.2, style='solid')
            continue
        # Determine direction
        if f >= 0:
            src, dst = i, j
            fmag = f
        else:
            src, dst = j, i
            fmag = -f
        (x1, y1) = pos[src]
        (x2, y2) = pos[dst]
        # shorten arrows so they don't overlap nodes
        shrink = 0.04
        dx = x2 - x1
        dy = y2 - y1
        # width scaling
        if max_flow_abs > 0:
            width = 0.8 + 4.2 * (fmag / max_flow_abs)
        else:
            width = 1.5
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='-|>',
            mutation_scale=10 + 25 * (fmag / (max_flow_abs if max_flow_abs else 1)),
            linewidth=width,
            color=color,
            shrinkA=15, shrinkB=15,
            alpha=0.9
        )
        ax.add_patch(arrow)
        if show_edge_labels:
            xm = 0.5 * (x1 + x2)
            ym = 0.5 * (y1 + y2)
            ax.text(xm, ym, f"{f:.1f}", fontsize=7, color='black', ha='center', va='center', bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.6))

    # Colorbar for shedding
    if norm is not None:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Load Shedding (MW)')

    # Legends (edge status + example arrow scale)
    legend_elements = [
        Line2D([0], [0], color='gray', lw=2, label='Line'),
        Line2D([0], [0], color='green', lw=2, label='Defended'),
        Line2D([0], [0], color='red', lw=2, label='Disabled')
    ]
    if max_flow_abs > 0:
        legend_elements.append(Line2D([0], [0], color='black', lw=4, label=f'Max Flow ~ {max_flow_abs:.1f}'))
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8, framealpha=0.9)

    if result:
        shed_total = result.get('total_shed', 0.0)
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
            fig, ax = plt.subplots()
            plot_grid(model, res, disabled=res['disabled'], ax=ax)
            plt.show()
    interact(view, k=IntSlider(description='Attack k', min=0, max=max_attack, step=1, value=0))
    return out
