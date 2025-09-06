from typing import Dict, Tuple, List, Set, Optional
import pulp
import math
from .model import GridModel

# Decision variable naming helpers

def solve_dispatch_min_shed(model: GridModel, disabled_lines: Optional[Set[Tuple[int,int]]] = None):
    if disabled_lines is None:
        disabled_lines = set()
    prob = pulp.LpProblem('dispatch_min_shed', pulp.LpMinimize)
    buses = model.buses
    lines = [e for e in model.lines if (e not in disabled_lines and (e[1], e[0]) not in disabled_lines)]

    # variables
    theta = {i: pulp.LpVariable(f"theta_{i}", lowBound=model.theta_min, upBound=model.theta_max) for i in buses}
    g = {i: pulp.LpVariable(f"g_{i}", lowBound=model.g_min.get(i, 0.0), upBound=model.g_max.get(i, 0.0)) for i in buses}
    c = {i: pulp.LpVariable(f"c_{i}", lowBound=model.c_min.get(i, 0.0), upBound=model.c_max.get(i, 0.0)) for i in buses}
    shed = {i: pulp.LpVariable(f"shed_{i}", lowBound=0.0, upBound=model.demand.get(i,0.0)) for i in buses}

    # reference bus angle (slack)
    slack = buses[0]
    prob += theta[slack] == 0.0

    # objective: minimize total shed + small gen cost
    prob += pulp.lpSum([shed[i] for i in buses]) + 1e-3 * pulp.lpSum([model.gen_cost.get(i,0.0)*g[i] for i in buses])

    # power balance: generation + controllable consumption + net inflow = demand - shed
    # DC power flow: flow(i,j) = b_ij (theta_i - theta_j)
    for i in buses:
        inflow_terms = []
        for j in model.G.neighbors(i):
            if (i,j) in disabled_lines or (j,i) in disabled_lines:
                continue
            b = model.G[i][j]['b']
            inflow_terms.append(b*(theta[j] - theta[i]))  # inflow positive if angle_j > angle_i
        prob += g[i] - c[i] + pulp.lpSum(inflow_terms) == model.demand.get(i,0.0) - shed[i]

     # bus capacity constraints
    for i in buses:
        prob += g[i] <= model.g_max.get(i, 0.0)
        prob += g[i] >= model.g_min.get(i, 0.0)
        prob += c[i] >= model.c_min.get(i, 0.0)
        prob += c[i] <= model.c_max.get(i, 0.0)
    # line capacity constraints
    for (i,j) in lines:
        b = model.G[i][j]['b']
        cap = model.G[i][j]['capacity']
        flow_ij = b*(theta[i] - theta[j])
        prob += flow_ij <= cap
        prob += -flow_ij <= cap

    res = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[prob.status]
    # safe value extraction
    def v(x):
        val = x.value()
        return float(val) if val is not None else 0.0
    return {
        'status': status,
        'objective': float(pulp.value(prob.objective)) if pulp.value(prob.objective) is not None else math.inf,
        'g': {i: v(g[i]) for i in buses},
        'c': {i: v(c[i]) for i in buses},
        'theta': {i: v(theta[i]) for i in buses},
        'shed': {i: v(shed[i]) for i in buses},
        'total_shed': float(sum(v(shed[i]) for i in buses)),
        'disabled': list(disabled_lines)
    }


def solve_attack_max_shed(model: GridModel, budget: int):
    # naive bilevel via enumeration (small grids) - choose up to budget lines to remove maximizing min-shed dispatch result
    import itertools
    best = None
    lines = model.lines
    for k in range(1, min(budget, len(lines)) + 1):
        for subset in itertools.combinations(lines, k):
            res = solve_dispatch_min_shed(model, set(subset))
            if best is None or res['total_shed'] > best['total_shed']:
                best = res
    if best is None:  # no attack
        best = solve_dispatch_min_shed(model, set())
    best['attack_budget'] = budget
    return best


def solve_defense_min_shed(model: GridModel, attack_budget: int, defend_budget: int):
    # simple heuristic: evaluate attacks and see which lines if defended reduce worst-case shed.
    # defend_budget lines can be protected (cannot be removed). We brute force defense subsets (small only)
    import itertools
    lines = model.lines
    best_def = None
    for def_subset in itertools.combinations(lines, min(defend_budget, len(lines))):
        protected = set(def_subset)
        worst_case = None
        # enumerate attacks ignoring protected lines
        attackable = [l for l in lines if l not in protected]
        for k in range(1, min(attack_budget, len(attackable)) + 1):
            for subset in itertools.combinations(attackable, k):
                res = solve_dispatch_min_shed(model, set(subset))
                if worst_case is None or res['total_shed'] > worst_case['total_shed']:
                    worst_case = res
        if worst_case is None:
            worst_case = solve_dispatch_min_shed(model, set())
        if best_def is None or worst_case['total_shed'] < best_def['worst_case']['total_shed']:
            best_def = {'defended': list(protected), 'worst_case': worst_case}
    if best_def is None:
        best_def = {'defended': [], 'worst_case': solve_dispatch_min_shed(model, set())}
    best_def['attack_budget'] = attack_budget
    best_def['defend_budget'] = defend_budget
    return best_def

