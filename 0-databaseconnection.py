import sqlite3
from typing import Optional, List, Tuple

class DatabaseConnection:
    """Custom context manager for database connections"""
    
    def __init__(self, db_name: str = ":memory:"):
        self.db_name = db_name
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def __enter__(self):
        """Open database connection when entering context"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {self.db_name}")
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close database connection when exiting context"""
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        
        if self.connection:
            if exc_type is None:  # No exception occurred
                self.connection.commit()
                print("Changes committed")
            else:
                self.connection.rollback()
                print("Changes rolled back due to exception")
            
            self.connection.close()
            print("Connection closed")
        
        # Return False to propagate exceptions, True to suppress them
        return False

# Example usage with the context manager
def main():
    # Create an in-memory database for demonstration
    with DatabaseConnection(":memory:") as cursor:
        # Create a sample users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        
        # Insert some sample data
        sample_users = [
            (1, "Alice Johnson", "alice@example.com"),
            (2, "Bob Smith", "bob@example.com"),
            (3, "Charlie Brown", "charlie@example.com")
        ]
        
        cursor.executemany("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", sample_users)
        print("Sample data inserted")
        
        # Perform the required query: SELECT * FROM users
        cursor.execute("SELECT * FROM users")
        
        # Fetch and print the results
        results = cursor.fetchall()
        print("\nResults from SELECT * FROM users:")
        print("-" * 50)
        print(f"{'ID':<5} {'Name':<15} {'Email':<20}")
        print("-" * 50)
        
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20}")
        
        print("-" * 50)
        print(f"Total users: {len(results)}")

if __name__ == "__main__":
    main()
