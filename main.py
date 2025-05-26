import json
import sys
import numpy as np
from simulate import simulate
import config

def compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations=100, confidence=95):
    all_percentiles = []
    for _ in range(num_simulations):
        data, _, _ = simulate(qs, total_orders)
        percentiles = np.percentile(data, percentages)
        all_percentiles.append(percentiles)

    all_percentiles = np.array(all_percentiles)
    lower_bound = np.percentile(all_percentiles, (100 - confidence) / 2, axis=0).tolist()
    upper_bound = np.percentile(all_percentiles, 100 - (100 - confidence) / 2, axis=0).tolist()
    return lower_bound, upper_bound

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_simulation.py output")
        exit(1)

    output_path = f"output/{sys.argv[1]}.json"
    # percentages = np.arange(90.0, 100.0, 0.05).tolist()
    percentages = list(range(1, 101))
    total_orders = config.TOTAL_ORDERS
    num_simulations = config.NUM_SIMULATIONS
    # loss_rates = [0.005]
    loss_rates = [0, 0.00005, 0.0005, 0.001, 0.005]
    qs = 100

    results = {
        "percentages": percentages,
        "qs": qs,
        "results_by_loss_rate": {}
    }

    for lr in loss_rates:
        config.LOSS_RATE = lr
        data, _, _ = simulate(qs, total_orders)
        cdf = np.percentile(data, percentages).tolist()
        lower, upper = None, None
        if lr > 0: lower, upper = compute_confidence_intervals(simulate, qs, total_orders, percentages, num_simulations)

        for elem, p in zip(cdf, percentages):
            if (elem > 0):
                print("non-zero lateness until ", p, f"(={elem})")
                break

        results["results_by_loss_rate"][str(lr)] = {
            "cdf": cdf,
            "ci_lower": lower,
            "ci_upper": upper
        }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("Written in : ", output_path)
if __name__ == "__main__":
    main()
