import sys
import numpy as np
import matplotlib.pyplot as plt
from simulate import simulate
import config

def compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations=100, confidence=95):
    """
    Compute confidence intervals by repeatedly calling `simulate`.
    """
    all_percentiles = []
    for _ in range(num_simulations):
        data = simulate(qs, total_orders)
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
    num_simulations = 50  # Number of times to call simulate for confidence intervals

    for qs in range(5, 30, 5):
        # Generate data for the main CDF
        data = simulate(qs, total_orders)
        cdf = np.percentile(data, percentages)

        # Compute confidence intervals using new data from simulate
        lower, upper = compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations)

        # Plot CDF
        plt.plot(cdf, percentages, label=f"qs={qs}")
        # Plot confidence intervals as a shaded region
        plt.fill_betweenx(percentages, lower, upper, alpha=0.2)

    plt.xlabel("Lateness")
    plt.ylabel("CDF")
    plt.legend(loc="best")
    plt.grid(True)
    plt.savefig(f"figs/{filename}")

if __name__ == "__main__":
    main()
