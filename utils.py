from collections import defaultdict
import random
from typing import TYPE_CHECKING, List
from order import Order

def find_longest_common_subsequence(o1: List[int], o2: List[int]):
    n, m = len(o1), len(o2)

    # Create a 2D DP table with dimensions (n+1) x (m+1) initialized to 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Fill the DP table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if o1[i - 1] == o2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # The length of the longest common subsequence is in dp[n][m]
    return dp[n][m]


## Following were used instead of LOQ to double check the code
def shuffle_orders_per_price_group(orders: List[Order]) -> List[Order]:
    # Group orders by price
    price_groups = defaultdict(list)
    for order in orders:
        price_groups[order.price].append(order)

    # Shuffle each price group individually
    for price, group in price_groups.items():
        random.shuffle(group)

    # Flatten the shuffled groups back into a single list
    shuffled_orders = [order for group in price_groups.values() for order in group]

    return shuffled_orders

def windowed_shuffle(orders: List[Order], win: int=10):
    for i in range(0, len(orders), win):
        window = orders[i:i+win]
        random.shuffle(window)
        orders[i:i+win] = window
    return orders

def create_random_halves(orders: List[Order]):
    a = []
    b = []
    for o in orders:
        if random.choice([True, False]):  # Randomly choose a list
            a.append(o)
        else:
            b.append(o)
    return a, b

def create_halves(orders: List[Order]):
    a = []
    b = []
    t = True
    for o in orders:
        if t: a.append(o)
        else: b.append(o)
        t = not t    
    return a, b
