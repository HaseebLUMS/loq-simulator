import copy
from typing import List
import argparse
import numpy as np
from LOB import LimitOrderBook
from order import Order
import random
import utils
import config
import LOQ

########################## Configuring LOQ version ##########################
LOQ_EMULATION_MAP = {
    3: LOQ.emulate_loq_v3,  # loq w/o mid-price in tuple
    4: LOQ.emulate_loq_v4  # low w mid-price in tuple
}
LOQ_EMULATION = LOQ_EMULATION_MAP.get(config.LOQ_VERSION, LOQ.emulate_loq_v3)
##########################            End            ##########################


# Create m sequence of trading orders, each sequence has n orders
def create_order_sequences(n: int, m: int) -> List[List[Order]]:
    bid_range = list(range(config.BID_RANGE[0], config.BID_RANGE[1]+1))
    ask_range = list(range(config.ASK_RANGE[0], config.ASK_RANGE[1]+1))

    sequences: List[List[Order]] = []

    for client in range(0, m):
        timestamp = 1  # Start timestamps from 1
        orders: List[Order] = []
        for order_id in range(1, n + 1):
            # Randomly choose side as 'bid' or 'ask'
            side = 'bid' if random.choice([True, False]) else 'ask'

            # Set price based on side
            price = random.choice(bid_range) if side == 'bid' else random.choice(ask_range)

            quantity = 1

            # Create order
            order = Order(
                order_id=(client << 32) | order_id,
                side=side,
                price=price,
                quantity=quantity,
                timestamp=timestamp,
                tmp=client,
                I_m=0)
            orders.append(order)

            # Increment timestamp for the next order
            timestamp += 1

        sequences.append(orders)
    return sequences

def simulate_centralized_engine(orders: List[List[Order]]) -> List[int]:
    input_orders_l1: List[List[Order]] = copy.deepcopy(orders)
    reordered_orders_l1 = list(map(emulate_network_link, input_orders_l1))
    input_orders_l2: List[List[Order]] = []
    index = 0
    while index < len(reordered_orders_l1):
        input_orders_l2.append(LOQ.combine_orders_from_downstreams(
            [reordered_orders_l1[index], reordered_orders_l1[index+1]]))
        index += 2
    reordered_orders_l2 = list(map(emulate_network_link, input_orders_l2))
    reordered_orders = LOQ.combine_orders_from_downstreams(reordered_orders_l2)
    lob = LimitOrderBook()
    for o in reordered_orders: lob.add_order(o)
    return lob.get_matched_orders_sequence()

def emulate_network_link(stream: List[Order]):
    if config.NETWORK_REORDERING:
        REORDERING_FACTOR = 100
        for i in range(len(stream)):
            start = i
            end = min(i + REORDERING_FACTOR, len(stream))
            
            sub_window = stream[start:end]
            random.shuffle(sub_window)
            
            stream[start:end] = sub_window
    return stream

'''
A tree with depth 3 is used. Bottom-most level (l1) contains config.TOTAL_LOQS proxies. 
Second last level (l2) contains config.TOTAL_LOQS/2 proxies. Third last (i,e, top) level 
contains the root/matching engine. 

The above topology is hardcoded as we just need some topo to simulate distributed engine. 

Each proxy runs an LOQ. The orders traverse up the tree. 
'''
def simulate_distributed_engine(orders: List[List[Order]], queue_size: int) -> List[int]:
    input_orders_l1: List[List[Order]] = copy.deepcopy(orders)

    # Feed the sequence(s) to an LOQ emulater, which reorders the sequence emulating 
    # how an LOQ at a proxy would do it. Each list in reordered_orders_l1 represents the output from a proxy
    reordered_orders_l1: List[List[Order]] = []
    for h in input_orders_l1: reordered_orders_l1.append(LOQ_EMULATION(h, win=int((queue_size/100)*len(h))))

    # Output of proxies is sent to parent proxies travelling through the network. So we apply network link
    # emulation to output of each proxy
    reordered_orders_l1 = list(map(emulate_network_link, reordered_orders_l1))

    # Combine every two loqs output into one sequence (representing two proxies feeding their output to a parent proxy)
    input_orders_l2: List[List[Order]] = []
    index = 0
    while index < len(reordered_orders_l1):
        input_orders_l2.append(LOQ.combine_orders_from_downstreams(
            [reordered_orders_l1[index], reordered_orders_l1[index+1]]))
        index += 2

    # Do the same with input_orders_l2 as we did with input_orders_l1
    reordered_orders_l2: List[List[Order]] = []
    for h in input_orders_l2: reordered_orders_l2.append(LOQ_EMULATION(h, win=int((queue_size/100)*len(h))))

    reordered_orders_l2 = list(map(emulate_network_link, reordered_orders_l2))

    # Combine all the orders from the l2 proxies into one sequence representing how they are fed to ME
    reordered_orders = LOQ.combine_orders_from_downstreams(reordered_orders_l2)

    # Feed then reordered sequence to ME and get the output
    lob = LimitOrderBook()
    for o in reordered_orders: lob.add_order(o)
    return lob.get_matched_orders_sequence()

'''
Given the sequences representing in what order all the trading orders got matched, 
it checks whether the orders in `distributed` were late (and by how much).
If an order was the i-th order to get matched in the centralized version and it was
j-th order to get matched in the distributed version, then the lateness of this order is |j-i|
'''
def compare_matched_orders(centralized: List[int], distributed: List[int]):
    t1 = {}
    t2 = {}
    for i, o in enumerate(centralized): t1[o] = i
    for i, o in enumerate(distributed): t2[o] = i

    res = {}
    data = []
    for o in t1:
        if o in t2:
            late = abs(t2[o] - t1[o])
        else:
            late = 1000  # just a large penalty if o is not in t2

        res[o] = late
        data.append(late)

    if config.LOGGING:
        print("50p Lateness: ", np.percentile(data, 50))
        print("90p Lateness: ", np.percentile(data, 90))
        print("99p Lateness: ", np.percentile(data, 99))

    return data

'''
Simulates centralized and distributed matching engine

Args:
queue_size denotes the size of queue (of orders) that builds up at each proxy.  queue_size=x means
a proxy will have a queue of size equal to x% of all the orders 
(total_orders/# of proxies in the last layer) that a proxy processes. 

total_orders denotes the total orders used for the simulation. 
'''
def simulate(queue_size=None, total_orders=None):
    queue_size = queue_size if queue_size is not None else config.QUEUE_SIZE
    total_orders = total_orders if total_orders is not None else config.TOTAL_ORDERS

    orders_sequences = create_order_sequences(total_orders, config.TOTAL_LOQS)
    centralized_output = simulate_centralized_engine(orders_sequences)
    distributed_output = simulate_distributed_engine(orders_sequences, queue_size)

    return compare_matched_orders(centralized_output, distributed_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some orders.")
    parser.add_argument(
        "--queue_size", "-qs",
        type=int,
        help="Size of the queue",
    )
    parser.add_argument(
        "--total_orders", "-to",
        type=int,
        help="Total number of orders",
    )

    args = parser.parse_args()

    simulate(queue_size=args.queue_size, total_orders=args.total_orders)
