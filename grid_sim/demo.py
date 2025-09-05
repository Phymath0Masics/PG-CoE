from .random_gen import random_grid
from .opt import solve_dispatch_min_shed, solve_attack_max_shed, solve_defense_min_shed
from .viz import plot_grid
import matplotlib.pyplot as plt


def quick_demo():
    model = random_grid(8, 0.4, seed=2)
    base = solve_dispatch_min_shed(model)
    print('Base shed', base['total_shed'])
    attack = solve_attack_max_shed(model, budget=2)
    print('Attack shed', attack['total_shed'], 'disabled', attack['disabled'])
    defense = solve_defense_min_shed(model, attack_budget=2, defend_budget=2)
    print('Defense chooses', defense['defended'], 'worst-case shed', defense['worst_case']['total_shed'])
    fig, axs = plt.subplots(1,3, figsize=(15,4))
    plot_grid(model, base, ax=axs[0])
    plot_grid(model, attack, disabled=attack['disabled'], ax=axs[1])
    plot_grid(model, defense['worst_case'], disabled=defense['worst_case']['disabled'], defended=defense['defended'], ax=axs[2])
    axs[0].set_title('Baseline')
    axs[1].set_title('Attack')
    axs[2].set_title('Defense worst-case')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    quick_demo()
