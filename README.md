Run `python3 main.py`


# Initial Results

If asks and bid price range only overlap at a single point, then the behavior of LOQ and FIFO is exactly the same in terms of matched orders. (not in terms of received orders)


bids = 1, 2, 3
asks = 3, 4, 5

100% same matched orders


If they overlap at various points (which means a lot of asks and bids are crossing the midprice by several steps), then the behavior diverges and depends on the queue size. 


bids = 1, 2, 3
asks = 2, 3, 4

queue size = 0 % of all orders

100% the sequence of matched orders is same across LOQ and FIFO


queue size = 10 % of all orders

80% to 90% the sequence of matched orders is same across LOQ and FIFO


queue size = 20 % of all orders

50% to 80% the sequence of matched orders is same across LOQ and FIFO


queue size = 50 % of all orders

40% the sequence of matched orders is same across LOQ and FIFO

# TODO

More LOQs (e.g., 2 in front of LOB)
- a sequence, randomly split across two LOQs

- two designs: everythong on fpga, compute scale of exchange
- increase order throughput (where the bottleneck is)
- homa (incast)
- core wise scalablity (speedex?)

send repo link to anirudh

point anirudh to databento APIs/offering

Compare both LOQ+LOB and LOB with repsect the time of order amtching 

-- Formalize it! Start writing a proof

CCAC, venkat

cmac -> a model for queue position evaluation in lob