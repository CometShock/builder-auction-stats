import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
import matplotlib.ticker as ticker
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process the bids for a specified builder_pubkey.')
parser.add_argument('--builder_pubkey', default='0x945fc51bf63613257792926c9155d7ae32db73155dc13bdfe61cd476f1fd2297b66601e8721b723cef11e4e6682e9d87', help='the builder_pubkey to process')
args = parser.parse_args()

# Connect to your postgres DB
conn = psycopg2.connect(dbname='builder_bids_db', user='postgres', password='postgres', host='localhost', port=5432)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
cur.execute(f"SELECT MAX(highest_value)*1e-18 as max_bid, slot FROM best_bids WHERE builder_pubkey='{args.builder_pubkey}' GROUP BY slot ORDER BY slot DESC")

# Retrieve query results
rows = cur.fetchall()

# Create a DataFrame from the fetched rows
df = pd.DataFrame(rows, columns=['max_bid', 'slot'])

# Check the data type of 'max_bid'
print("Data type of max_bid:", df['max_bid'].dtype)

# Check the contents of the DataFrame
print(df)

# Convert 'max_bid' to a numeric data type, if it isn't already
if not pd.api.types.is_numeric_dtype(df['max_bid']):
    df['max_bid'] = pd.to_numeric(df['max_bid'], errors='coerce')

# Sort the DataFrame by 'slot'
df.sort_values('slot', inplace=True)

# Create a stem plot
plt.stem(df['slot'], df['max_bid'], markerfmt=' ', basefmt="b-")

# Customize the plot
plt.title(f'{args.builder_pubkey}', fontsize=6)
plt.suptitle("Specified Block Builder's Max Bid for Each Slot")
plt.xlabel('Slot')
plt.ylabel('Max Bid (ETH)')
plt.grid(axis='y')  # Add a horizontal grid for better readability

# Set the number of ticks you want to display on the x-axis (adjust this as needed)
num_ticks = 10
# Determine the step size for the x-axis ticks
step_size = max(1, len(df) // num_ticks)

# Get the indices for the x-axis ticks
x_ticks_indices = range(0, len(df), step_size)

# Get the corresponding 'slot' values for the x-axis ticks
x_tick_labels = df['slot'].iloc[x_ticks_indices]

# Set the x-axis ticks and labels
plt.xticks(x_tick_labels, rotation=90)

# Format the x-axis tick labels to show the entire integer without scientific notation
plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

plt.show()
