import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(dbname='builder_bids_db', user='postgres', password='postgres', host='localhost', port=5432)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
cur.execute("SELECT DISTINCT builder_pubkey FROM best_bids")

# Retrieve query results
rows = cur.fetchall()

print(rows)
