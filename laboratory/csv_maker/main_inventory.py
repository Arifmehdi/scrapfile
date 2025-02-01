import mysql.connector
from collections import defaultdict
import sys

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dreamcar"
)
cursor = conn.cursor(dictionary=True)



# Retrieve all data from the TmpDealer model for batch_no 101
cursor.execute("SELECT * FROM tmp_dealers WHERE batch_no = 100")
tmp_dealers = cursor.fetchall()


# Retrieve existing inventory where VIN is not null and group by dealer_id
cursor.execute("SELECT deal_id, vin, dealer_id FROM main_inventories WHERE vin IS NOT NULL")
inventory_data = cursor.fetchall()


existing_inventory_by_dealer = defaultdict(list)
for row in inventory_data:
    existing_inventory_by_dealer[row["dealer_id"]].append(row["vin"])

# Initialize lists
inventory_sold = []
inventory_added = []
csvVINsByDealer = {}

tmp_imported = []
tmp_updated = []
tmp_skipped = []

imported = []
updated = []
skipped = []

# Fetch all inventory with dealer info
cursor.execute("SELECT * FROM MainInventory")
inventory = cursor.fetchall()

# Get the latest batch number
cursor.execute("SELECT batch_no FROM MainInventory ORDER BY batch_no DESC LIMIT 1")
latest_batch = cursor.fetchone()
batch_no = latest_batch["batch_no"] + 1 if latest_batch else 101

# Close the cursor and connection
cursor.close()
conn.close()

print("Batch No:", batch_no)
