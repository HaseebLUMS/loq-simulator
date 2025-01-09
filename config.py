BID_RANGE = [1,6]
ASK_RANGE = [2,7]
MID_PRICE = 4
ACTION_WINDOW = 2


# For prev loq
# BID_RANGE = [1,5]
# ASK_RANGE = [5,9]
# MID_PRICE = 5
# ACTION_WINDOW = 0

TOTAL_ORDERS = 10_000

# Overwritten in main.py
QUEUE_SIZE = 10  # as percentage of all the orders, 50 denotes 50% of the orders are queued at a time

TOTAL_LOQS = 10

LOGGING = False
##### Just verifying some configs ##########
assert len(BID_RANGE) == 2
assert len(ASK_RANGE) == 2
assert (MID_PRICE+ACTION_WINDOW == BID_RANGE[1])
assert (MID_PRICE-ACTION_WINDOW == ASK_RANGE[0])
assert (MID_PRICE-ACTION_WINDOW >= BID_RANGE[0])
assert (MID_PRICE+ACTION_WINDOW <= ASK_RANGE[1])
assert (TOTAL_LOQS%2 == 0)  # there will be `TOTAL_LOQS` in the last level and `TOTAL_LOQS/2` in the second last level