import sqlite3

connection = sqlite3.connect("driverbase.db")
cursor = connection.cursor()

cursor.execute("create table ")

connection.close()