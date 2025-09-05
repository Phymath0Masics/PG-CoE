# PG-CoE (simulation of cyber security in power grid system)

## grid_sim – Attack/Defense DC Power Flow Sandbox

Lightweight Python framework for experimenting with a tri‑level (defense–attack–operation) formulation on power transmission networks using a DC approximation. Provides random grid generation, optimal dispatch (min load shedding), brute‑force attacker and heuristic defender, plus plotting, animation, and notebook widgets.

## Features
- GridModel dataclass (buses, lines, bounds, demand, costs)
- Random grid generator (`random_grid`)
- DC dispatch minimizing total shedding (`solve_dispatch_min_shed`)
- Brute‑force attack enumerator (`solve_attack_max_shed`)
- Heuristic defense enumeration (`solve_defense_min_shed`)
- Matplotlib static plots, per‑edge flow thickness & color
- Simple animation (`animate_attack_defense`) & interactive widget (`interactive_attack_defense`)
- Reproducible scenario export

## Installation
Create / activate a virtual environment, then install deps.
```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Quick Start
```python
from python_codes.grid_sim import random_grid, solve_dispatch_min_shed
model = random_grid(10, 0.4, seed=1)
res = solve_dispatch_min_shed(model)
print(res['total_shed'])
```

### Visual
```python
from python_codes.grid_sim.viz import plot_grid
plot_grid(model, res)
```

### Attack & Defense
```python
from python_codes.grid_sim import solve_attack_max_shed, solve_defense_min_shed
atk = solve_attack_max_shed(model, budget=2)
def_plan = solve_defense_min_shed(model, attack_budget=2, defend_budget=2)
```

## Notebook Widget
```python
from python_codes.grid_sim.viz import interactive_attack_defense
interactive_attack_defense(model, max_attack=4)
```

## Usage Catalog (Matches notebook examples)
1. Random grid + dispatch  
2. Manual grid construction  
3. Single attack scenario  
4. Sweep attack budgets  
5. Defense planning  
6. Baseline / attack / defense plots  
7. Interactive attack explorer  
8. Animation of history  
9. Batch statistics  
10. Defense budget sensitivity  
11. Specific outage evaluation  
12. Extract flows  
13. Slack bus note  
14. Custom solver placeholder  
15. Export model data  
16. Attack budgets on defended network  
17. DataFrame view  
18. Script entry  
19. Monte Carlo defense value  
20. Vulnerability placeholder  
21. Scenario record  
22. Heuristic critical‑line removal  
23. Serialize to JSON  
24. Zero‑shed check  
25. Baseline flow plot  

## Model Formulation (Dispatch Level)
Minimize sum of load shedding variables subject to:  
- Nodal balance (g − c + shed = sum of incident DC flows)  
- Flow = b_ij (θ_i − θ_j)  
- Line capacity limits  
- Bounds on generation, controllable consumption, angles, shedding  
Slack bus angle fixed at 0.

## Attack / Defense Abstraction
Attack: select up to A lines to disable (enumeration).  
Defense: choose up to D lines to protect, then worst‑case attack evaluated over remaining lines.  
Current implementation brute‑forces (small networks). For larger systems, replace with MILP or heuristics.

## Architecture
```
python_codes/grid_sim/
  model.py        # GridModel dataclass
  random_gen.py   # random_grid()
  opt.py          # solve_dispatch_min_shed / attack / defense
  viz.py          # plot_grid, animation, widgets
  demo.py         # quick showcase script
```

## Extending
- Replace brute force with MILP bilevel: introduce binary outage vars & big‑M linking.
- Import MATPOWER cases (parse .m to populate GridModel).
- Add cost minimization objective variant.
- Islanding detection & shedding distribution rules.
- Parallel enumeration (multiprocessing) for attacks.

## Performance Notes
Brute force grows combinatorially: O(∑ C(|E|,k)). Keep |E| small (< ~25) or limit budgets. For larger graphs, implement heuristics.

## Limitations
- DC approximation only (no reactive power, voltages).
- No contingency cascading or dynamic stability modeling.
- Defense and attack solved by enumeration; not scalable.
- Single angle reference; no automatic island handling.

## Roadmap (Proposed)
1. MILP attacker via binary line status.
2. Unified tri‑level single‑level reformulation (KKT + dualization) for small systems.
3. MATPOWER importer utility.
4. Flow‑based criticality metrics ranking.
5. CLI & simple web dashboard.

## Testing
Add unit tests for: nodal balance residuals, line limit enforcement, attack enumeration correctness, defense improvement monotonicity.

## Data Export
`GridModel.export_data()` returns dict: buses, lines (i,j,b,cap), bounds, demand; suitable for JSON serialization.

## License
Project code: (add chosen license, e.g., MIT).  
MATPOWER data (if used) remains under its original license (see `matpower8.1/LICENSE`).

## Citation / Credits
- MATPOWER project for test case inspiration.  
- PuLP & CBC for LP solving.  
- NetworkX for graph handling.

## Disclaimer
Prototype research tool—not production grade. Validate results against a trusted OPF solver before drawing conclusions.

## Quick Demo Command
```powershell
python -m python_codes.grid_sim.demo
```

