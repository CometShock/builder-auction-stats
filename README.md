# builder-auction-stats

An unpolished scrappy approach to collect MEV-Boost Builder Auction data, store it in a PostgreSQL database, and generate analytics using the collected data.

Currently pulls nearly-live data from each MEV-Boost block relay every 12 seconds, keeping pace with slots.

### Nuances
If the proposer for the next slot is not registered with the relay, the relay will not serve any data responses for that slot (except Flashbots relay).
In practice, this means that a relay's data response with 0 entries is signaling that the proposer for that slot is not registered. Either the proposer is a vanilla block builder, or they are selectively registered with only *some* of the other relays.

### Future Work
- Error detection & handling in data collection
- Filling in vanilla block data
- Live dashboard
- Accessible scripts & functions
  - Backfill data collection (from a reference block/slot)
  - Custom windowed stats
  - Custom builder selection
  - Rolling window stats with custom rolling width
- [REDACTED] ;)
