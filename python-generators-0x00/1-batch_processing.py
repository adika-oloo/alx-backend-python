#!/usr/bin/python3
"""
Batch processing for large datasets - filters users over age 25
"""

import mysql.connector
import os
from typing import Dict, Any, Generator, List

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator that fetches rows from user_data table in batches
    
    Args:
        batch_size: Number of rows to fetch in each batch
        
    Yields:
        List: Batch of user records as dictionaries
    """
    connection = None
    cursor = None
    
    try:
        # Database configuration
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
        
        # Execute query
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        
        # First loop: yield batches until no more rows
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
            
    except mysql.connector.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size: int = 100) -> None:
    """
    Processes batches of users and filters those over age 25
    
    Args:
        batch_size: Number of users to process in each batch
    """
    import sys
    
    try:
        # Second loop: iterate over batches from generator
        for batch_num, batch in enumerate(stream_users_in_batches(batch_size), 1):
            # Third loop: process each user in the batch
            for user in batch:
                # Filter users over age 25
                if user['age'] > 25:
                    print(user)
            
            # Optional: Print progress for large datasets
            if batch_num % 10 == 0:
                print(f"Processed {batch_num} batches...", file=sys.stderr)
                
    except Exception as e:
        print(f"Processing error: {e}", file=sys.stderr)
        raise

# Alternative implementation with age filtering in database query (more efficient)
def batch_processing_optimized(batch_size: int = 100) -> None:
    """
    Optimized version that filters by age at database level
    """
    import sys
    
    def stream_filtered_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generator that fetches only users over age 25 in batches
        """
        connection = None
        cursor = None
        
        try:
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': 'ALX_prodev',
                'port': os.getenv('DB_PORT', '3306')
            }
            
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            
            # Filter at database level for better performance
            query = "SELECT user_id, name, email, age FROM user_data WHERE age > 25"
            cursor.execute(query)
            
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                yield batch
                
        except mysql.connector.Error as e:
            print(f"Database error: {e}", file=sys.stderr)
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    try:
        # Only one loop needed in this optimized version
        for batch_num, batch in enumerate(stream_filtered_users_in_batches(batch_size), 1):
            for user in batch:
                print(user)
                
            if batch_num % 10 == 0:
                print(f"Processed {batch_num} batches...", file=sys.stderr)
                
    except Exception as e:
        print(f"Processing error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    # Test with small batch size when run directly
    batch_processing(10)
