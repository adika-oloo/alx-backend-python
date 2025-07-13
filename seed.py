# seed.py

import mysql.connector
import os

def connect_db():
    """Connects to the MySQL server (no database selected)."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PWD", "yourpassword"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )

def connect_to_prodev():
    """Connects specifically to the ALX_prodev database."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PWD", "yourpassword"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        database="ALX_prodev"
    )

def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX(user_id)
        );
    """)
    print("Table user_data created successfully")
    cursor.close()

def insert_data(connection, csv_file):
    import csv
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_data;")
    if cursor.fetchone()[0] > 0:
        print("Data already exists in user_data table.")
        return

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute(
                "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                (row['user_id'], row['name'], row['email'], row['age'])
            )
    connection.commit()
    print("Data inserted successfully")
    cursor.close()
