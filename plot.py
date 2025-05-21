import json
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

mpl.rcParams['font.size'] = 18
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

def plot_from_json(json_path, output_filename):
    with open(json_path) as f:
        results = json.load(f)

    percentages = results["percentages"]
    qs = results["qs"]
    results_by_lr = results["results_by_loss_rate"]

    fig, ax = plt.subplots(figsize=(8, 6))

    for lr_str, data in results_by_lr.items():
        lr = float(lr_str)
        cdf = data["cdf"]
        lower = data["ci_lower"]
        upper = data["ci_upper"]

        ax.plot(cdf, percentages, label=f"loss rate={lr * 100:.03f}%", linewidth=2)
        if lower and upper:
            ax.fill_betweenx(percentages, lower, upper, alpha=0.2)

    ax.set_xlabel("Lateness")
    ax.set_ylabel("CDF")
    ax.legend(loc="best")
    ax.grid(True)
    for spine in ax.spines.values():
        spine.set_edgecolor('lightblue')

    # Inset
    axins = inset_axes(ax, width="40%", height="40%", loc='upper right', borderpad=2)
    for data in results_by_lr.values():
        cdf = data["cdf"]
        axins.plot(cdf, percentages, linewidth=2)

        lower = data["ci_lower"]
        upper = data["ci_upper"]
        if lower and upper:
            axins.fill_betweenx(percentages, lower, upper, alpha=0.1)

    axins.set_xlim(-1, 20)
    axins.set_ylim(80, 102)
    axins.tick_params(labelsize=22)

    plt.tight_layout()
    plt.savefig(f"figs/{output_filename}.pdf", bbox_inches='tight')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python plot_results.py results.json output_name")
        exit(1)
    plot_from_json(sys.argv[1], sys.argv[2])