import matplotlib as mpl

mpl.rcParams['font.size'] = 18  # Change 12 to your desired font size
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42


import sys
import numpy as np
import matplotlib.pyplot as plt
from simulate import simulate
import config

def compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations=100, confidence=95):
    # return None, None
    """
    Compute confidence intervals by repeatedly calling `simulate`.
    """
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
    if (len(sys.argv) < 2):
        print("Provide output filename e.g., tmp.pdf")
        exit(1)

    filename = sys.argv[1]
    percentages = list(range(1, 101))
    total_orders = config.TOTAL_ORDERS
    num_simulations = config.NUM_SIMULATIONS  # Number of times to call simulate, for confidence intervals
    loss_rates = [0.0001, 0.0005, 0.001, 0.005]

    for qs in range(100, 101):  # Trying several Queue Sizes
        for lr in loss_rates:
            config.LOSS_RATE = lr
            # Generate data for the main CDF
            data, sells, buys = simulate(qs, total_orders)  # The main simulation code
            cdf = np.percentile(data, percentages)

            # Compute confidence intervals using new data from simulate
            lower, upper = compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations)

            # Plot CDF
            plt.plot(cdf, percentages, label=f"loss rate={config.LOSS_RATE*100}%", linewidth=2)
            # Plot confidence intervals as a shaded region
            if lower is not None:
                plt.fill_betweenx(percentages, lower, upper, alpha=0.2)
            

            # # # for buys and sells
            # values = sorted(list(sells.values()))
            # print("sells: ", values)
            # values = sorted(list(buys.values()))
            # print("buys: ", values)

    plt.xlabel("Lateness")
    plt.ylabel("CDF")
    plt.legend(loc="best")
    # plt.grid(True)
    # plt.show()
    plt.savefig(f"figs/{filename}.pdf")

if __name__ == "__main__":
    main()
