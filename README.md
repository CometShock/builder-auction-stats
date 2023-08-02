# builder-auction-stats

An unpolished scrappy approach to collect MEV-Boost Builder Auction data, store it in a PostgreSQL database, and generate analytics using the collected data.

Currently pulls nearly-live data from each MEV-Boost block relay every 12 seconds (keeping pace with slots). Current analysis is running crude case studies on specific block builders and their best bids for each slot. Does not yet filter out bids that come after a proposer already selected a bid.

### Nuances
If the proposer for the next slot is not registered with the relay, the relay will not serve any data responses for that slot.
In practice, this means that a relay's data response with 0 entries is signaling that the proposer for that slot is not registered. Either the proposer is a vanilla block builder, or they are selectively registered with only *some* of the other relays.

## Installation and Usage
1. Launch PostgreSQL, this repository assumes these defaults: `user='postgres', password='postgres', host='localhost', port=5432`
2. Clone this repository
3. In a terminal, navigate to the repository `builder-auction-stats`
4. Run `python3 collection/purge-db.py`, which purges the previous 'builder_bids_db' PostgreSQL database if it exists, and then (re)creates it.
5. Run `python3 collection/collect-bids.py` in your terminal to continuously collect live bids. Note the first slot number you collected from.
6. After at least 30 seconds, in a separate terminal run `python3 processing/best-bid.py --start_slot YOUR_FIRST_SLOT_NUMBER_HERE` to process the best bids from each builder, per slot.
7. best-bid.py does terminate once it caught up to collect-bids.py, but notes the slot it finished at. You can run it again with just `python3 processing/best-bid.py` and it should pick up from where it left off.
8. Run `python3 analytics/builder-case.py` to display a case study plot of a single block builder's highest bid for each slot you have collected data from. You can optionally specify the builder pubkey that you want to analyze with `python3 analytics/builder-case.py --builder_pubkey 'YOUR_DESIRED_BUILDER_PUBKEY_HERE'`

### Dependencies
- pandas
- psycopg2
- matplotlib
- argparse

### Future Work
- Error detection & handling in data collection
- Block Delivered Payload Data
  - Collect Data
  - Run analysis to compare timestamps, winning bid vs case builder's bid, etc
- Filling in vanilla block data
- Live dashboard
- More efficient data handling for large sets
- Accessible scripts, functions, options
  - Backfill data collection (from a reference block/slot)
  - Custom windowed stats
  - Call out builder names rather than pubkeys where applicable
  - Rolling window stats with custom rolling width
- Eliminate some duplicate entries bleeding through in best_bids Table
- [REDACTED] ;)
