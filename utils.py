from typing import TYPE_CHECKING, List

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