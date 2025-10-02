import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    A class-based context manager for handling database connections.
    
    This context manager automatically opens and closes database connections,
    and provides convenient methods for executing queries.
    """
    
    def __init__(self, db_path='users.db', timeout=30.0, isolation_level=None):
        """
        Initialize the database connection context manager.
        
        Args:
            db_path (str): Path to the SQLite database file
            timeout (float): Timeout for database operations in seconds
            isolation_level: SQLite isolation level (None for autocommit, 'DEFERRED', 'IMMEDIATE', 'EXCLUSIVE')
        """
        self.db_path = db_path
        self.timeout = timeout
        self.isolation_level = isolation_level
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        """
        Enter the context manager - opens the database connection.
        
        Returns:
            DatabaseConnection: self instance for method chaining
        """
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                isolation_level=self.isolation_level
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Database connection opened: {self.db_path}")
            return self
        except sqlite3.Error as e:
            logger.error(f"Failed to open database connection: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - closes the database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.cursor:
            self.cursor.close()
            logger.debug("Database cursor closed")
            
        if self.connection:
            if exc_type is not None:
                # An exception occurred - rollback any changes
                self.connection.rollback()
                logger.info("Transaction rolled back due to exception")
            else:
                # No exception - commit any changes
                self.connection.commit()
                logger.info("Transaction committed successfully")
                
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query, parameters=None):
        """
        Execute a SQL query and return all results.
        
        Args:
            query (str): SQL query to execute
            parameters (tuple): Query parameters for prepared statements
            
        Returns:
            list: Query results
        """
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
                
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query, parameters=None):
        """
        Execute an UPDATE, INSERT, or DELETE query.
        
        Args:
            query (str): SQL query to execute
            parameters (tuple): Query parameters for prepared statements
            
        Returns:
            int: Number of affected rows
        """
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
                
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Update execution failed: {e}")
            raise
    
    def get_column_names(self):
        """
        Get column names from the last executed query.
        
        Returns:
            list: Column names
        """
        if self.cursor.description:
            return [description[0] for description in self.cursor.description]
        return []

# Enhanced version with more features
class AdvancedDatabaseConnection(DatabaseConnection):
    """
    Enhanced database connection context manager with additional features.
    """
    
    def __init__(self, db_path='users.db', timeout=30.0, isolation_level=None, row_factory=None):
        """
        Initialize the advanced database connection.
        
        Args:
            row_factory: Row factory for custom row objects (e.g., sqlite3.Row)
        """
        super().__init__(db_path, timeout, isolation_level)
        self.row_factory = row_factory
    
    def __enter__(self):
        """
        Enter the context manager with enhanced features.
        """
        connection = super().__enter__()
        
        # Set row factory if specified
        if self.row_factory:
            self.connection.row_factory = self.row_factory
            
        return connection
    
    def execute_many(self, query, parameters_list):
        """
        Execute the same query multiple times with different parameters.
        
        Args:
            query (str): SQL query to execute
            parameters_list (list): List of parameter tuples
            
        Returns:
            int: Total number of affected rows
        """
        try:
            self.cursor.executemany(query, parameters_list)
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Execute many failed: {e}")
            raise
    
    def execute_script(self, script):
        """
        Execute a SQL script containing multiple statements.
        
        Args:
            script (str): SQL script to execute
        """
        try:
            self.cursor.executescript(script)
        except sqlite3.Error as e:
            logger.error(f"Script execution failed: {e}")
            raise
    
    def get_table_info(self, table_name):
        """
        Get information about a table's schema.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            list: Table schema information
        """
        return self.execute_query(f"PRAGMA table_info({table_name})")

# Example usage and demonstration
if __name__ == "__main__":
    print("=== Basic Database Connection Example ===")
    
    # Example 1: Basic usage with SELECT query
    try:
        with DatabaseConnection('users.db') as db:
            # Execute the SELECT * FROM users query
            results = db.execute_query("SELECT * FROM users")
            column_names = db.get_column_names()
            
            print(f"Column names: {column_names}")
            print(f"Number of users: {len(results)}")
            
            # Print all results
            for row in results:
                print(row)
                
    except Exception as e:
        print(f"Database operation failed: {e}")
    
    print("\n=== Advanced Database Connection Example ===")
    
    # Example 2: Advanced usage with sqlite3.Row for dict-like access
    try:
        with AdvancedDatabaseConnection('users.db', row_factory=sqlite3.Row) as db:
            results = db.execute_query("SELECT * FROM users")
            column_names = db.get_column_names()
            
            print(f"Column names: {column_names}")
            print("Users (as dictionaries):")
            
            for row in results:
                # Convert Row to dict for easy access
                user_dict = dict(row)
                print(user_dict)
                
    except Exception as e:
        print(f"Advanced database operation failed: {e}")
    
    print("\n=== Multiple Operations in Single Context ===")
    
    # Example 3: Multiple operations in a single context
    try:
        with DatabaseConnection('users.db') as db:
            # Get user count
            count_result = db.execute_query("SELECT COUNT(*) FROM users")
            print(f"Total users: {count_result[0][0]}")
            
            # Get active users
            active_users = db.execute_query("SELECT * FROM users WHERE active = 1")
            print(f"Active users: {len(active_users)}")
            
            # Example of an update (commented out to avoid modifying data)
            # updated = db.execute_update(
            #     "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", 
            #     (1,)
            # )
            # print(f"Updated {updated} user(s)")
            
    except Exception as e:
        print(f"Multiple operations failed: {e}")
    
    print("\n=== Error Handling Example ===")
    
    # Example 4: Error handling demonstration
    try:
        with DatabaseConnection('users.db') as db:
            # This will cause an error (table doesn't exist)
            results = db.execute_query("SELECT * FROM nonexistent_table")
    except sqlite3.OperationalError as e:
        print(f"Expected error handled: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
