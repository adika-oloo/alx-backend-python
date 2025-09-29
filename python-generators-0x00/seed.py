#!/usr/bin/python3
"""
Database seeder and generator for ALX_prodev user_data
"""

import mysql.connector
import csv
import os
import uuid
from typing import Generator, Tuple, Any

def connect_db() -> mysql.connector.connection.MySQLConnection:
    """
    Connects to the MySQL database server
    
    Returns:
        MySQLConnection: Database connection object
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '3306')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection: mysql.connector.connection.MySQLConnection) -> None:
    """
    Creates the database ALX_prodev if it does not exist
    
    Args:
        connection: MySQL connection object
    """
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def connect_to_prodev() -> mysql.connector.connection.MySQLConnection:
    """
    Connects to the ALX_prodev database in MySQL
    
    Returns:
        MySQLConnection: Database connection object
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database='ALX_prodev',
            port=os.getenv('DB_PORT', '3306')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def create_table(connection: mysql.connector.connection.MySQLConnection) -> None:
    """
    Creates a table user_data if it does not exist with the required fields
    
    Args:
        connection: MySQL connection object
    """
    cursor = connection.cursor()
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def insert_data(connection: mysql.connector.connection.MySQLConnection, csv_file: str) -> None:
    """
    Inserts data from CSV file into the database if it does not exist
    
    Args:
        connection: MySQL connection object
        csv_file: Path to the CSV file containing user data
    """
    cursor = connection.cursor()
    try:
        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("Data already exists in the table. Skipping insertion.")
            return
        
        # Read CSV and insert data
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if exists
            
            insert_query = """
            INSERT IGNORE INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            
            batch_data = []
            for row in csv_reader:
                if len(row) >= 4:
                    # Generate UUID if not provided in CSV
                    user_id = row[0] if row[0] else str(uuid.uuid4())
                    name = row[1]
                    email = row[2]
                    age = float(row[3]) if row[3] else 0
                    
                    batch_data.append((user_id, name, email, age))
            
            # Insert in batches for better performance
            batch_size = 100
            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                cursor.executemany(insert_query, batch)
                connection.commit()
            
            print(f"Inserted {len(batch_data)} records successfully")
            
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        connection.rollback()
    finally:
        cursor.close()

def stream_users(connection: mysql.connector.connection.MySQLConnection) -> Generator[Tuple[Any, ...], None, None]:
    """
    Generator that streams rows from user_data table one by one
    
    Args:
        connection: MySQL connection object
        
    Yields:
        Tuple: A row from the user_data table
    """
    cursor = None
    try:
        # Use a server-side cursor for efficient memory usage with large datasets
        cursor = connection.cursor(buffered=False)
        
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
            
    except mysql.connector.Error as e:
        print(f"Error streaming data: {e}")
    finally:
        if cursor:
            cursor.close()

def stream_users_batch(connection: mysql.connector.connection.MySQLConnection, batch_size: int = 100) -> Generator[list, None, None]:
    """
    Generator that streams rows in batches for better performance
    
    Args:
        connection: MySQL connection object
        batch_size: Number of rows to fetch at once
        
    Yields:
        List: Batch of rows from the user_data table
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield rows
            
    except mysql.connector.Error as e:
        print(f"Error streaming data in batches: {e}")
    finally:
        if cursor:
            cursor.close()

def get_user_count(connection: mysql.connector.connection.MySQLConnection) -> int:
    """
    Get total number of users in the database
    
    Args:
        connection: MySQL connection object
        
    Returns:
        int: Total number of users
    """
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM user_data")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
