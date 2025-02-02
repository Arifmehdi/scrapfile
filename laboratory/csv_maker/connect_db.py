import mysql.connector

# Database connection details
config = {
    # "host": localhost",  # Your Cloudways server host
    # "port": 8082,  # Use the port specified in your URL
    "host": "host",  # Public IP of your server
    "port": 3306,  # Change if your database uses a different port
    "user": "user",  # Your database username
    "password": "your_pass",  # Your database password
    "database": "your-db"  # Your database name
}

try:
    # Establish connection
    conn = mysql.connector.connect(**config)
    if conn.is_connected():
        print("✅ Connected to the database!")

    # Example query
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    print("Tables in the database:")
    for table in tables:
        print(table[0])

    # Close connection
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
