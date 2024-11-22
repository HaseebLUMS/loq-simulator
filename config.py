BID_RANGE = [1, 5]
ASK_RANGE = [5, 9]

TOTAL_ORDERS = 1000
QUEUE_SIZE = 10  # as percentage of all the orders, 50 denotes 50% of the orders are queued at a time


##### Just verifying some configs ##########
assert len(BID_RANGE) == 2
assert len(ASK_RANGE) == 2