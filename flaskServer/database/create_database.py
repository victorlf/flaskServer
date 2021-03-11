import sqlite3

conn = sqlite3.connect('database/measurements.db')
print("Opened database successfully")

#conn.execute('CREATE TABLE measurements (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor TEXT NOT NULL, temperature TEXT NOT NULL, pressure TEXT NOT NULL)')
conn.execute("DROP TABLE IF EXISTS temp_pres")
conn.execute('CREATE TABLE temp_pres (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor TEXT NOT NULL, temperature NUMERIC NOT NULL, pressure NUMERIC NOT NULL, timestamp DATETIME NOT NULL)')
print("Table created successfully")
conn.close()
