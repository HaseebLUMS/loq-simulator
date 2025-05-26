import json
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.size'] = 18
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

# Global thresholds
PRACTICAL_LOSSES = 1  # example index or threshold (like 2nd point on x-axis)
PRACTICAL_DELAYS = 3  # example index or threshold (like 4th point on x-axis)

def plot_avg_lateness(json_path, output_filename):
    with open(json_path) as f:
        results = json.load(f)

    results_by_lr = results["results_by_loss_rate"]

    # Prepare data
    lr_labels = []
    avg_90p_lateness = []
    avg_50p_lateness = []

    for lr_str, data in sorted(results_by_lr.items(), key=lambda x: float(x[0])):
        lr_labels.append(f"{float(lr_str) * 100:.3f}")
        lateness_90p = data["cdf"][89]
        lateness_50p = data["cdf"][49]
        avg_90p_lateness.append(lateness_90p)
        avg_50p_lateness.append(lateness_50p)

    # X-axis positions
    x_positions = list(range(len(lr_labels)))

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(
        x_positions,
        avg_90p_lateness,
        'o-',
        linewidth=3,
        label="90p Lateness"
    )

    ax.plot(
        x_positions,
        avg_50p_lateness,
        's--',
        linewidth=3,
        label="50p Lateness"
    )

    # Highlight practical loss area (red, light)
    if PRACTICAL_LOSSES < len(x_positions):
        ax.axvspan(
            x_positions[0],
            PRACTICAL_LOSSES,
            color='green',
            alpha=0.2,
            # label="Practical Losses Area"
        )

    # # Highlight practical delay area (blue, light)
    # if PRACTICAL_DELAYS < len(x_positions):
    #     ax.axvspan(
    #         x_positions[0],
    #         PRACTICAL_DELAYS,
    #         color='green',
    #         alpha=0.2,
    #         # label="Practical Delays Area"
    #     )

    ax.set_xlabel("Loss Rate (%)")
    ax.set_ylabel("Lateness")
    ax.grid(True)
    ax.legend(loc="best")
    for spine in ax.spines.values():
        spine.set_edgecolor('lightblue')

    ax.set_xticks(x_positions)
    ax.set_xticklabels(lr_labels, rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(f"figs/{output_filename}.pdf", bbox_inches='tight')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python plot_avg_lateness.py results.json output_name")
        exit(1)
    plot_avg_lateness(f"output/{sys.argv[1]}.json", sys.argv[2])
