#!/usr/bin/python3
"""
Generator that streams rows from user_data table one by one
"""

import mysql.connector
import os
from typing import Dict, Any, Generator

def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that streams rows from user_data table one by one
    
    Yields:
        Dict: A dictionary representing a single row from user_data table
    """
    connection = None
    cursor = None
    
    try:
        # Database connection parameters
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': 'ALX_prodev',
            'port': os.getenv('DB_PORT', '3306')
        }
        
        # Connect to database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query - using server-side cursor for memory efficiency
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        
        # Single loop to yield rows one by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
            
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Alternative implementation with context managers (more Pythonic)
def stream_users_v2() -> Generator[Dict[str, Any], None, None]:
    """
    Alternative implementation using context managers for automatic resource cleanup
    """
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': 'ALX_prodev',
        'port': os.getenv('DB_PORT', '3306')
    }
    
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT user_id, name, email, age FROM user_data")
                
                # Single loop as required
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                    yield row
                    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        raise


# For backward compatibility with the test script
if __name__ == "__main__":
    # Test the generator
    for i, user in enumerate(stream_users()):
        print(user)
        if i >= 5:  # Limit output for testing
            break
