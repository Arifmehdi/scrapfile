import mysql.connector

def get_mysql_connection():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'dreamcar',
    }

    conn = mysql.connector.connect(**db_config)
    return conn