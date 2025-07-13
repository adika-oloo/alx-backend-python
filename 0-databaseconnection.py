
"""
Custom context manager for handling MySQL database connections.
"""

import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Establish connection and return cursor."""
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """Close cursor and connection, handle exceptions."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        # Return False to propagate exceptions if any
        return False


# Example usage
if __name__ == "__main__":
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "yourpassword", 
        "database": "ALX_prodev"
    }

    try:
        with DatabaseConnection(**db_config) as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            for row in results:
                print(row)
    except Error as e:
        print(f"Database error: {e}")
