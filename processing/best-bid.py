import psycopg2

# Connect to the PostgreSQL server
conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port=5432)
cur = conn.cursor()

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

# Get the highest slot number currently in the best_bids table
cur.execute("SELECT MAX(slot) FROM best_bids")
max_slot = cur.fetchone()[0]

if max_slot is None:
    max_slot = 0  # If best_bids is empty, start from the beginning

# Get the most recent slot - 2 in the builder_bids table
cur.execute("SELECT MAX(slot) - 2 FROM builder_bids")
most_recent_slot_minus_two = cur.fetchone()[0]

# If there's no data in builder_bids yet, or all slots up to most_recent_slot_minus_two are already in best_bids, we're done
if most_recent_slot_minus_two is None or most_recent_slot_minus_two <= max_slot:
    print("No new slots to update.")
else:
    # Insert into best_bids the highest bids for each builder_pubkey in each slot from max_slot + 1 to most_recent_slot_minus_two
    cur.execute("""
        INSERT INTO best_bids (slot, builder_pubkey, highest_value, url)
        SELECT slot, builder_pubkey, MAX(value), url
        FROM builder_bids
        WHERE slot > %s AND slot <= %s
        GROUP BY slot, builder_pubkey, url
    """, (max_slot, most_recent_slot_minus_two))

    # Commit the transaction
    conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()
