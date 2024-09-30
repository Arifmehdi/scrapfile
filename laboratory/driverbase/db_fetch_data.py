import sqlite3

def fetch_all_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('driverbase_data.db')
    cursor = conn.cursor()

    # # Fetch all dealers
    # cursor.execute('SELECT * FROM dealers')
    # dealers = cursor.fetchall()
    
    # print("Dealers:")
    # for dealer in dealers:
    #     print(f"ID: {dealer[0]}, Dealer ID:{dealer[1]}, Dealer Title: {dealer[2]}, Radius: {dealer[3]}, Phone: {dealer[4]},  Address: {dealer[5]}, Listing Info: {dealer[6]}, Status Details: {dealer[7]}, Dealer Custom URL: {dealer[8]}, Website Link: {dealer[9]}")
    
    print("\nInventories:")
    # Fetch all inventories
    cursor.execute('SELECT * FROM vehicles')
    inventories = cursor.fetchall()
    
    for inventory in inventories:
        # print(f"ID: {inventory[0]}, Dealer ID: {inventory[1]}, Inventory Link: {inventory[2]}")
        print(inventory)
    
    # print("\nInventory Details:")
    # # Fetch all inventory details
    # cursor.execute('SELECT * FROM inventory_details')
    # inventory_details = cursor.fetchall()
    
    # for detail in inventory_details:
    #     print(f"ID: {detail[0]}, Inventory ID: {detail[1]}, Detail Key: {detail[2]}, Detail Value: {detail[3]}")
    
    # Close the connection
    conn.close()

# Call the function to fetch and display data
fetch_all_data()
