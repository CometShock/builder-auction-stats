import requests
import time
import json
import psycopg2
from datetime import datetime, timedelta

# PostgreSQL connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',  # or the IP address of your PostgreSQL server
    'port': 5432  # or the port your PostgreSQL server is listening on
}

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(**db_params)

# Create a cursor object
cur = conn.cursor()
# list of your API URLs
urls = [
    "https://0xac6e77dfe25ecd6110b8e780608cce0dab71fdd5ebea22a16c0205200f2f8e2e3ad3b71d3499c54ad14d6c21b41a37ae@boost-relay.flashbots.net",
	"https://0x8b5d2e73e2a3a55c6c87b8b6eb92e0149a125c852751db1422fa951e42a09b82c142c3ea98d0d9930b056a3bc9896b8f@bloxroute.max-profit.blxrbdn.com",
	"https://0xad0a8bb54565c2211cee576363f3a347089d2f07cf72679d16911d740262694cadb62d7fd7483f27afd714ca0f1b9118@bloxroute.ethical.blxrbdn.com",
	"https://0xb0b07cd0abef743db4260b0ed50619cf6ad4d82064cb4fbec9d3ec530f7c5e6793d9f286c4e082c0244ffb9f2658fe88@bloxroute.regulated.blxrbdn.com",
	"https://0x9000009807ed12c1f08bf4e81c6da3ba8e3fc3d953898ce0102433094e5f22f21102ec057841fcb81978ed1ea0fa8246@builder-relay-mainnet.blocknative.com",
	"https://0xb3ee7afcf27f1f1259ac1787876318c6584ee353097a50ed84f51a1f21a323b3736f271a895c7ce918c038e4265918be@relay.edennetwork.io",
	"https://0x98650451ba02064f7b000f5768cf0cf4d4e492317d82871bdc87ef841a0743f69f0f1eea11168503240ac35d101c9135@mainnet-relay.securerpc.com",
	"https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
	"https://0xa7ab7a996c8584251c8f925da3170bdfd6ebc75d50f5ddc4050a6fdc77f2a3b5fce2cc750d0865e05d7228af97d69561@agnostic-relay.net",
	"https://0xa15b52576bcbf1072f4a011c0f99f9fb6c66f3e1ff321f11f461d15e31b1cb359caa092c71bbded0bae5b5ea401aab7e@aestus.live"
    # add more URLs as needed
]

# This is your reference time and slot off of which you schedule requests.
# Feel free to tweak this in order to get closer to the live slot, but beware
# asking on the live slot as you may not get complete data.
reference_time = datetime(2023, 7, 15, 12, 22, 13)
reference_slot = 6884808

def calculate_current_slot():
    current_time = datetime.now()
    time_difference = current_time - reference_time
    seconds_difference = int(time_difference.total_seconds())
    
    # Since one slot corresponds to 12 seconds
    slots_difference = seconds_difference // 12
    
    current_slot = reference_slot + slots_difference
    return current_slot

def calculate_next_slot_time(current_slot):
    next_slot = current_slot + 1
    slots_difference = next_slot - reference_slot
    seconds_difference = slots_difference * 12
    next_slot_time = reference_time + timedelta(seconds=seconds_difference)
    return next_slot_time

# Initialize current_slot with the slot corresponding to the current time
current_slot = calculate_current_slot()

while True:  # infinite loop
    start_time = datetime.now()  # get the current time at the start of the loop

    for url in urls:
        # append endpoint and slot to base URL
        full_url = f"{url}/relay/v1/data/bidtraces/builder_blocks_received?slot={current_slot}"
        response = requests.get(full_url)
        
        if response.status_code == 200:  # HTTP OK
            bid_traces = response.json()  # parse JSON data from response
            
            print(f"slot {current_slot}: Received {len(bid_traces)} entries on from {url}")
            
            for bid_trace in bid_traces:  # iterate over each bid trace
                # Extract values from the JSON data
                slot = bid_trace.get('slot')
                parent_hash = bid_trace.get('parent_hash')
                block_hash = bid_trace.get('block_hash')
                builder_pubkey = bid_trace.get('builder_pubkey')
                proposer_fee_recipient = bid_trace.get('proposer_fee_recipient')
                gas_limit = bid_trace.get('gas_limit')
                gas_used = bid_trace.get('gas_used')
                value = bid_trace.get('value')
                block_number = bid_trace.get('block_number')
                num_tx = bid_trace.get('num_tx')
                timestamp = bid_trace.get('timestamp')
                timestamp_ms = bid_trace.get('timestamp_ms')

                # Insert the data into the database
                cur.execute("""
                    INSERT INTO builder_bids (slot, parent_hash, block_hash, builder_pubkey, proposer_fee_recipient,
                                           gas_limit, gas_used, value, block_number, num_tx, timestamp, timestamp_ms,
                                           url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (slot, parent_hash, block_hash, builder_pubkey, proposer_fee_recipient, gas_limit, gas_used,
                      value, block_number, num_tx, timestamp, timestamp_ms, url))
                
                # Commit the transaction
                conn.commit()
                
        else:
            print(f"Request to {full_url} failed with status code {response.status_code}.")

    # Calculate the start time of the next slot
    next_slot_time = calculate_next_slot_time(current_slot)
    time_until_next_slot = (next_slot_time - datetime.now()).total_seconds()

    # If there's time remaining until the next slot, wait that amount of time
    if time_until_next_slot > 0:
        time.sleep(time_until_next_slot)

    # Increment the slot for the next round
    current_slot += 1

