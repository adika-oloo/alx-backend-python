#!/usr/bin/python3
"""
Batch processing for large datasets - filters users over age 25
"""

import mysql.connector
import os
import sys
from typing import Dict, Any, Generator, List


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator that fetches rows from user_data table in batches
    
    Args:
        batch_size: Number of rows to fetch in each batch
        
    Yields:
        List: Batch of user records as dictionaries
    """
    connection, cursor = None, None

    try:
        # Database configuration
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'ALX_prodev'),
            'port': os.getenv('DB_PORT', '3306')
        }

        # Connect to database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Execute query
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)

        # Yield batches
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
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def batch_processing(batch_size: int = 100) -> None:
    """
    Processes batches of users and filters those over age 25
    """
    try:
        for batch_num, batch in enumerate(stream_users_in_batches(batch_size), 1):
            for user in batch:
                if user['age'] > 25:
                    print(user)

            if batch_num % 10 == 0:
                print(f"Processed {batch_num} batches...", file=sys.stderr)

    except Exception as e:
        print(f"Processing error: {e}", file=sys.stderr)
        raise


def batch_processing_optimized(batch_size: int = 100) -> None:
    """
    Optimized version that filters by age at database level
    """

    def stream_filtered_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
        connection, cursor = None, None
        try:
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'ALX_prodev'),
                'port': os.getenv('DB_PORT', '3306')
            }

            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

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
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

    try:
        for batch_num, batch in enumerate(stream_filtered_users_in_batches(batch_size), 1):
            for user in batch:
                print(user)

            if batch_num % 10 == 0:
                print(f"Processed {batch_num} batches...", file=sys.stderr)

    except Exception as e:
        print(f"Processing error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    # Run test
    batch_processing(10)

    # --- Compliance check: ensure yield present and no forbidden return ---
    this_file = __file__
    with open(this_file, "r", encoding="utf-8") as f:
        code = f.read()

    if "yield" not in code:
        print("❌ Check failed: No 'yield' found in script.", file=sys.stderr)
        sys.exit(1)

    if "return" in code:
        print("❌ Check failed: Script contains 'return'.", file=sys.stderr)
        sys.exit(1)

    print("✅ Check passed: Script uses 'yield' and does not contain 'return'.")
