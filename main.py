import matplotlib as mpl

mpl.rcParams['font.size'] = 18
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

import sys
import numpy as np
import matplotlib.pyplot as plt
from simulate import simulate
import config
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle

def compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations=100, confidence=95):
    # return None, None
    all_percentiles = []
    for _ in range(num_simulations):
        data, _, _ = simulate(qs, total_orders)
        percentiles = np.percentile(data, percentages)
        all_percentiles.append(percentiles)

    all_percentiles = np.array(all_percentiles)
    lower_bound = np.percentile(all_percentiles, (100 - confidence) / 2, axis=0)
    upper_bound = np.percentile(all_percentiles, 100 - (100 - confidence) / 2, axis=0)
    return lower_bound, upper_bound

def main():
    if len(sys.argv) < 2:
        print("Provide output filename e.g., tmp.pdf")
        exit(1)

    filename = sys.argv[1]
    percentages = list(range(1, 101))
    total_orders = config.TOTAL_ORDERS
    num_simulations = config.NUM_SIMULATIONS
    loss_rates = [0, 0.00005, 0.0005, 0.005]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Cache for main plot and inset
    cdf_data_by_lr = {}
    ci_bounds_by_lr = {}  # Store (lower, upper) per loss rate

    for qs in range(100, 101):
        for lr in loss_rates:
            config.LOSS_RATE = lr
            data, sells, buys = simulate(qs, total_orders)
            cdf = np.percentile(data, percentages)
            lower, upper = compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations)

            ax.plot(cdf, percentages, label=f"loss rate={config.LOSS_RATE * 100:.03f}%", linewidth=2)
            if lower is not None:
                ax.fill_betweenx(percentages, lower, upper, alpha=0.2)

            cdf_data_by_lr[lr] = cdf
            ci_bounds_by_lr[lr] = (lower, upper)

    ax.set_xlabel("Lateness")
    ax.set_ylabel("CDF")
    ax.legend(loc="best")
    ax.grid(True)
    for spine in ax.spines.values():
        spine.set_edgecolor('lightblue')

    # Inset zoom box
    axins = inset_axes(ax, width="40%", height="40%", loc='upper right', borderpad=2)
    for lr in loss_rates:
        cdf = cdf_data_by_lr[lr]
        axins.plot(cdf, percentages, linewidth=2)

        # Optional: confidence interval in inset too
        lower, upper = ci_bounds_by_lr[lr]
        if lower is not None:
            axins.fill_betweenx(percentages, lower, upper, alpha=0.1)

    axins.set_xlim(-1, 20)
    axins.set_ylim(80, 102)
    axins.tick_params(labelsize=8)

    # # Optional: Add red rectangle to show zoom region
    # zoom_rect = Rectangle((0, 80), 20, 22, linewidth=1, edgecolor='red', facecolor='none')
    # ax.add_patch(zoom_rect)

    plt.tight_layout()
    plt.savefig(f"figs/{filename}.pdf", bbox_inches='tight')

if __name__ == "__main__":
    main()
