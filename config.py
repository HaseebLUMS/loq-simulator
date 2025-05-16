# LOQ specific configs
BID_RANGE = [1,5]
ASK_RANGE = [3,7]
MID_PRICE = 4
ACTION_WINDOW = 1
QUEUE_SIZE = 10  # as percentage of all the orders, 50 denotes 50% of the orders are queued at a time. Overwritten in main.py
TOTAL_LOQS = 10

# 3

LOQ_VERSION = 4  # 3 is the latest version
LOSS_RATE = 0.5 # * 100 percent, so 0.05 means 5 percent
LOSSY_CLIENTS = [0]  # leave empty for making all lossy

# Experiment specific
NUM_SIMULATIONS = 10
TOTAL_ORDERS = 1000

LOGGING = True
NETWORK_REORDERING = False  # As we use TCP, so it should stay False

##### Just verifying some configs ##########
assert len(BID_RANGE) == 2
assert len(ASK_RANGE) == 2
assert (MID_PRICE+ACTION_WINDOW == BID_RANGE[1])
assert (MID_PRICE-ACTION_WINDOW == ASK_RANGE[0])
assert (MID_PRICE-ACTION_WINDOW >= BID_RANGE[0])
assert (MID_PRICE+ACTION_WINDOW <= ASK_RANGE[1])
assert (TOTAL_LOQS%2 == 0)  # there will be `TOTAL_LOQS` in the last level and `TOTAL_LOQS/2` in the second last level
