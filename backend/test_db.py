import mysql.connector
from mysql.connector import Error

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # <-- Replace with your actual MySQL password
        database='aicare'                # <-- Your database name
    )

    if conn.is_connected():
        print("✅ Successfully connected to the database!")
    else:
        print("❌ Connection failed.")

except Error as e:
    print(f"Error: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("Connection closed.")
