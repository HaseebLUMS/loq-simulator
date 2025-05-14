from datetime import datetime
import random
from typing import TYPE_CHECKING, List

import config

class Order:
    def __init__(
            self, order_id: str, side: str,
            price: int, quantity: int,
            timestamp: int, client: int, I_m):
        self.order_id = order_id
        self.side = side  # 'bid' or 'ask'
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp or int(datetime.now().timestamp() * 1_000_000)
        self.client = client  # basically client ID
        self.tmp = client  # it becomes the proxy ID so that an upstream sequencer can sequence streams from downstream proxies
        self.I_m = I_m  #  mid-price ID

    def __repr__(self):
        return f"Order(id={self.order_id}, I_m={self.I_m})"
        # return f"Order(id={self.order_id}, side={self.side}, price={self.price}, quantity={self.quantity}, timestamp={self.timestamp})"

    def __lt__(self, other):
        """Define less-than for automatic sorting by timestamp within SortedList."""
        if self.timestamp == other.timestamp: return self.client < other.client
        return self.timestamp < other.timestamp

def simulate_loss(rate) -> int:
    '''with probability `rate`, it returns 1 i.e., drop. otherwise 0'''
    assert 0.0 <= rate <= 1.0
    return 1 if random.random() < rate else 0

# Create m sequence of trading orders, each sequence has n orders
def create_order_sequences(n: int, m: int) -> List[List[Order]]:
    bid_range = list(range(config.BID_RANGE[0], config.BID_RANGE[1]+1))
    ask_range = list(range(config.ASK_RANGE[0], config.ASK_RANGE[1]+1))

    sequences: List[List[Order]] = []

    total_losses = 0

    def reset_count(n):
        return 1
        # return n // 10

    I_ms: List[int] = []
    id = 0
    count = reset_count(n)
    for index in range(0, n):
        I_ms.append(id)
        count -= 1
        if (count == 0):
            count = reset_count(n)
            id += 1

    for client in range(0, m):
        timestamp = 1  # Start timestamps from 1
        orders: List[Order] = []
        I_m_id = 1
        for order_id in range(1, n + 1):
            # Randomly choose side as 'bid' or 'ask'
            side = 'bid' if random.choice([True, False]) else 'ask'

            # Set price based on side
            price = random.choice(bid_range) if side == 'bid' else random.choice(ask_range)

            quantity = 1

            if simulate_loss(rate=config.LOSS_RATE) == 0: I_m_id = order_id-1
            else: total_losses += 1

            # Create order
            order = Order(
                order_id=f"{client}.{order_id}.{I_m_id}",
                side=side,
                price=price,
                quantity=quantity,
                timestamp=timestamp,
                client=client,
                I_m=I_ms[I_m_id])

            orders.append(order)

            # Increment timestamp for the next order
            timestamp += 1

        sequences.append(orders)
    
    print("Loss rate: ", 100.0 * total_losses / (n*m))
    return sequences