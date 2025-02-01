import mysql.connector

# Database connection details
config = {
    # "host": "phplaravel-1194462-4226380.cloudwaysapps.com",  # Your Cloudways server host
    # "port": 8082,  # Use the port specified in your URL
    "host": "137.184.15.16",  # Public IP of your server
    "port": 3306,  # Change if your database uses a different port
    "user": "senpvmzmtj",  # Your database username
    "password": "v5FmVJrAnx",  # Your database password
    "database": "senpvmzmtj"  # Your database name
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
