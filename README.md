Run `python3 main.py tmp.pdf`
Resulting pdf will be stored in figs/ dir.

https://docs.google.com/document/d/1QJAVf6wlCF_94knkZrR-ONv-CLsmsfepj07lyaxkzhA/edit?usp=sharing

# Results Dec 03

A better strategy than round robin is needed and then a merge-sort type protocol is needed to consult multiple queues

# Results Dec 02

Having multiple LOQs leads to some unfairness even when asks and bids price range overlap at a single point. Here is a scenario where it can happen:

LOQ1 has orders with timestamps: 1, 2, 3
LOQ2 has orders with timestamps: 4, 5, 6
Now ME shoudl not process orders as they are recieved, all orders from LOQ1 shoudl be processed before any order from the LOQ2. We do not have a protocol for that.  OR the d_s parameter takes care of it. It does not actually. need a protocol like i simulate in `counter_local_loq_effect`.
It's working well when there is only one price level i.e. bids range [1, 1]. But with more price levels, it is not giving the behavior i expected. 

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

- probably both loqs should be consulted simulatanously

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
