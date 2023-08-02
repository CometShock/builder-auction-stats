import psycopg2
import subprocess
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process the best bids starting from a specified slot.')
parser.add_argument('--start_slot', type=int, help='the slot number to start processing from')
args = parser.parse_args()

# Call distinct-builder.py script to update known builders
subprocess.run(["python3", "processing/distinct-builder.py"])

# Connect to the PostgreSQL server
conn = psycopg2.connect(dbname='builder_bids_db', user='postgres', password='postgres', host='localhost', port=5432)
cur = conn.cursor()

# Fetch known builders
cur.execute("SELECT builder_pubkey FROM all_builder_pubkeys")
known_builders = [row[0] for row in cur.fetchall()]

# Check if the best_bids table exists
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE  table_name = 'best_bids'
    )
""")
table_exists = cur.fetchone()[0]

# If it doesn't exist, create it
if not table_exists:
    cur.execute("""
        CREATE TABLE best_bids (
            slot INT NOT NULL,
            builder_pubkey TEXT NOT NULL,
            highest_value NUMERIC NOT NULL,
            url TEXT NOT NULL
        )
    """)
    conn.commit()
    print("Table 'best_bids' created")

# Start from the slot specified in the command line arguments, or from the highest slot number in the best_bids table if not specified
if args.start_slot:
    start_slot = args.start_slot
else:
    cur.execute("SELECT MAX(slot) FROM best_bids")
    max_slot = cur.fetchone()[0]
    start_slot = max_slot if max_slot else 0  # If best_bids is empty, start from the beginning

# Get the most recent slot - 2 in the builder_bids table
cur.execute("SELECT MAX(slot) - 2 FROM builder_bids")
most_recent_slot_minus_two = cur.fetchone()[0]

print(f"Starting from slot {start_slot + 1}")

# If there's no data in builder_bids yet, or all slots up to most_recent_slot_minus_two are already in best_bids, we're done
if most_recent_slot_minus_two is None or most_recent_slot_minus_two <= start_slot:
    print("No new slots to update.")
else:
    for slot in range(start_slot + 1, most_recent_slot_minus_two + 1):
        # Insert into best_bids the highest bids for each builder_pubkey in the slot
        cur.execute("""
            INSERT INTO best_bids (slot, builder_pubkey, highest_value, url)
            SELECT slot, builder_pubkey, MAX(value), url
            FROM builder_bids
            WHERE slot = %s
            GROUP BY slot, builder_pubkey, url
        """, (slot,))

        # For each known builder, if they don't have a bid in the slot, insert an entry with a highest_value of 0
        for builder in known_builders:
            cur.execute("""
                INSERT INTO best_bids (slot, builder_pubkey, highest_value, url)
                SELECT %s, %s, 0, 'N/A'
                WHERE NOT EXISTS (
                    SELECT 1 FROM best_bids WHERE slot = %s AND builder_pubkey = %s
                )
            """, (slot, builder, slot, builder))

        # Commit the transaction
        conn.commit()
        print(f"Updated slot {slot}")

    print(f"Updated to slot {most_recent_slot_minus_two}")

# Close the cursor and the connection
cur.close()
conn.close()
