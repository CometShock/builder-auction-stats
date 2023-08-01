import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port=5432)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
cur.execute("SELECT gas_used, timestamp FROM builder_bids ORDER BY timestamp DESC LIMIT 100")

# Retrieve query results
rows = cur.fetchall()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(rows, columns=["gas_used", "timestamp"])

# Convert the 'timestamp' column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Set the 'timestamp' column as the index
df.set_index('timestamp', inplace=True)

# Plot the 'gas_used' column
df['gas_used'].plot()

# Show the plot
plt.show()
