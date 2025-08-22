import sqlite3
from typing import Optional, List, Tuple, Any, Union

class ExecuteQuery:
    """Reusable context manager for executing database queries"""
    
    def __init__(self, db_name: str = ":memory:", query: str = "", params: tuple = ()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.results: Optional[List[Tuple]] = None
    
    def __enter__(self) -> List[Tuple]:
        """Execute the query when entering context and return results"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            # Execute the query with parameters
            self.cursor.execute(self.query, self.params)
            self.results = self.cursor.fetchall()
            
            print(f"Executed query: {self.query}")
            print(f"With parameters: {self.params}")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context"""
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            if exc_type is None:  # No exception occurred
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()
        
        # Return False to propagate exceptions
        return False

# Example usage with the context manager
def main():
    # First, let's set up a sample database with users table
    with sqlite3.connect(":memory:") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        
        # Insert sample data
        sample_users = [
            (1, "Alice Johnson", "alice@example.com", 30),
            (2, "Bob Smith", "bob@example.com", 22),
            (3, "Charlie Brown", "charlie@example.com", 35),
            (4, "Diana Prince", "diana@example.com", 28),
            (5, "Eve Davis", "eve@example.com", 19)
        ]
        
        cursor.executemany("INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)", sample_users)
        conn.commit()
    
    # Now use our reusable ExecuteQuery context manager
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    
    with ExecuteQuery(":memory:", query, params) as results:
        print(f"\nUsers older than 25:")
        print("-" * 50)
        print(f"{'ID':<5} {'Name':<15} {'Email':<20} {'Age':<5}")
        print("-" * 50)
        
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3]:<5}")
        
        print("-" * 50)
        print(f"Total users found: {len(results)}")

    # Reuse the same context manager with different parameters
    print("\n" + "="*60)
    
    with ExecuteQuery(":memory:", "SELECT * FROM users WHERE age < ?", (30,)) as young_users:
        print(f"\nUsers younger than 30:")
        print("-" * 50)
        for user in young_users:
            print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[3]}")

    # Reuse with a different query
    print("\n" + "="*60)
    
    with ExecuteQuery(":memory:", "SELECT name, email FROM users WHERE age BETWEEN ? AND ?", (25, 35)) as results:
        print(f"\nUsers between 25 and 35 years old:")
        print("-" * 40)
        for user in results:
            print(f"Name: {user[0]}, Email: {user[1]}")

if __name__ == "__main__":
    main()
