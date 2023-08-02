import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to the 'postgres' database
conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port=5432)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Drop the 'builder_bids_db' database
cur.execute("DROP DATABASE IF EXISTS builder_bids_db")
print("Database 'builder_bids_db' dropped")

# Recreate the 'builder_bids_db' database
cur.execute("CREATE DATABASE builder_bids_db")
print("Database 'builder_bids_db' recreated")

# Close the connection
cur.close()
conn.close()