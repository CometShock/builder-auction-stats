import psycopg2

# Connect to the PostgreSQL server
conn = psycopg2.connect(dbname='builder_bids_db', user='postgres', password='postgres', host='localhost', port=5432)
cur = conn.cursor()

# Check if the all_builder_pubkeys table exists
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE  table_name = 'all_builder_pubkeys'
    )
""")
table_exists = cur.fetchone()[0]

# If it doesn't exist, create it
if not table_exists:
    cur.execute("""
        CREATE TABLE all_builder_pubkeys (
            builder_pubkey TEXT NOT NULL PRIMARY KEY
        )
    """)
    conn.commit()
    print("Table 'all_builder_pubkeys' created")

# Insert distinct builder_pubkey values from builder_bids into all_builder_pubkeys
cur.execute("""
    INSERT INTO all_builder_pubkeys (builder_pubkey)
    SELECT DISTINCT builder_pubkey FROM builder_bids
    ON CONFLICT (builder_pubkey) DO NOTHING
""")
conn.commit()

print("Updated 'all_builder_pubkeys' with distinct builder_pubkeys from 'builder_bids'.")

# Close the cursor and the connection
cur.close()
conn.close()
