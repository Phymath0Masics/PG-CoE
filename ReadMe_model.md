### Power-Grid graphical model
a power grid graphical model is a graph $G = (V, E)$ where $V$ is the set of busses. Each $v\in V$ has both power consume $c_v$ and power supply $g_v$. A node $v\in V$ acts like a consumer if $c_v < g_v$ (usually for consumers $g_v=0$) and like a generator if $c_v > g_v$. $Y$ is the weighted adjacency matrix where $Y_{ij}$ is the admittance of the power line between nodes $i$ and $j$. In general we assign i-th vertex (bus) the phase angle $\theta_i$ and power generation $g_i$ and power consumption $c_i$ so that effective power gen is $p_i = g_i - c_i$. 

Thus we can express our power grid $G(V, E)$ in terms of the following ratings:

Line admittance matrix: $Y \in \mathbb{C}^{|E|\times |E|}$ matrix (it also contains information about the physical connections of the lines i.e. the graph adjacence matrix or the line avaiblity matrix $Z := \mathbb{1}_{\{Y\neq 0\}}$)

max and min phase angle vectors: $\theta^{max} = \{\theta_i^{max}\}, \theta^{min} = \{\theta_i^{min}\} \in \mathbb{R}^{|V|}$

max and min power generation rating vectors: $g^{max}=\{g_i^{max}\} \in \mathbb{R}^{|V|}, g^{min}=\{g_i^{min}\} \in \mathbb{R}^{|V|}$

max and min power consumption rating vectors: $c^{max}=\{c_i^{max}\} \in \mathbb{R}^{|V|}, c^{min}=\{c_i^{min}\} \in \mathbb{R}^{|V|}$ 

At the $i$-th node/bus the load shedding $s_i$ is defined from:
$$
g_i - c_i + s_i = \sum_{j\sim i} f_{ij} \implies g-c+s = L_Y\theta\,,\quad f_{ij} = Y_{ij} \left( \theta_i - \theta_j \right) \implies F = \{f_{ij}\} = diag(Y) A_G^\top \theta
$$
where $L_Y \in \mathbb{R}^{|V|\times |V|}$ is the laplacian of $Y$ and $A_G \in \{-1,0,1\}^{|V|\times |E|}$ is the signed node-edge incinence matrix (each column of $A_G$ has a +$1$ at the tail node and $−1$ at the head node) of graph $G$.

Since load shedding at a bus cann't be negative or greater than its demand/consumption, we have the bound $0 \leq s_i \leq c_i$. And hence the total load shedding in a power grid can be expressed as:
$$
S = \sum_{i \in V} s_i
$$

The goal is to find a configuration of optimal power flows that satisfies all consumer and generation demands while minimizing the total power loss (load shedding) in the network i.e.
$$
\min_{g, c, \theta, s} S
$$
such that $(g, c, \theta, s)$ satisfies:

the equalities (node balance and flow equation):
$$
g_i - c_i + s_i = \sum_{j\sim i} f_{ij} \implies g-c+s = L_Y\theta\,,\quad 
f_{ij} = Y_{ij}(\theta_i - \theta_j)
$$
and the inequalities (rating bounds)
$$
g \in [g^{min}, g^{max}]\,,\quad c \in [c^{min}, c^{max}]\,,\quad \theta \in [\theta^{min}, \theta^{max}]\,,\quad s \in [0, c^{max}]
$$

So we (i.e. the operator) have the power grid $G(V,E)$ with the rating dataset $(Y, g^{min}, g^{max}, c^{min}, c^{max}, \theta^{min}, \theta^{max})$ as input and we (the operator) have to find the optimal power flow operation i.e. the output $(g^*, c^*, \theta^*, s^*)$ which minimizes total load shedding $S$.

### Attack-Defend model
if $a_{ij} \in \{0, 1\}$ denotes attack on $ij$-th line and $d_{ij} \in \{0, 1\}$ denotes defense on $ij$-th line, the load flow equation becomes:
$$
f_{ij}' = z_{ij}f_{ij}\,,\quad z_{ij} = 1 - a_{ij}(1-d_{ij})
$$
So, $Z(a, d) = \{z_{ij}\}$ is the line availability matrix and $a, d \in \{0,1\}^{|E|}$. Note that both $a_{ij} = d_{ij} = 0$ whenever $Y_{ij} = 0$ i.e. there should be a physical line between buses $i$ and $j$.


### Main tri-level optimization formulation
Given the $n$-bus power grid graphical model $G=(V, E)$ and the attack-defend model with attack capacity $A$ and defence capacity $D$, we can formulate the following tri-level optimization problem to minimize load shedding while considering potential attacks and defenses on the power lines:
$$
\min_{d\in \{0,1\}^{|E|}, d^\top 1 \leq D} \max_{a\in \{0,1\}^{|E|}, a^\top 1 \leq A} \min_{g \in [g^{min}, g^{max}], c \in [c^{min}, c^{max}], \theta \in [\theta^{min}, \theta^{max}], s \in [0, c^{max}]} S
$$
