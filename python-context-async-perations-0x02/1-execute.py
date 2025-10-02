import sqlite3
import logging
from typing import Any, List, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecuteQuery:
    """
    A reusable context manager that executes SQL queries and manages database connections.
    
    This context manager takes a query and parameters, executes the query when entering
    the context, and automatically handles connection management.
    """
    
    def __init__(self, db_path: str = 'users.db', query: str = None, parameters: tuple = None):
        """
        Initialize the query execution context manager.
        
        Args:
            db_path (str): Path to the SQLite database file
            query (str): SQL query to execute
            parameters (tuple): Parameters for the SQL query
        """
        self.db_path = db_path
        self.query = query
        self.parameters = parameters
        self.connection = None
        self.cursor = None
        self.results = None
        
    def __enter__(self) -> 'ExecuteQuery':
        """
        Enter the context manager - opens connection and executes the query.
        
        Returns:
            ExecuteQuery: self instance with query results available
        """
        try:
            # Open database connection
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            logger.info(f"Database connection opened: {self.db_path}")
            
            # Execute the query if provided
            if self.query:
                self._execute_query()
                
            return self
            
        except sqlite3.Error as e:
            logger.error(f"Failed to open database connection or execute query: {e}")
            self._cleanup()
            raise
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit the context manager - closes the database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        try:
            if exc_type is not None:
                # An exception occurred - rollback any changes
                if self.connection:
                    self.connection.rollback()
                    logger.info("Transaction rolled back due to exception")
            else:
                # No exception - commit any changes
                if self.connection:
                    self.connection.commit()
                    logger.info("Transaction committed successfully")
        finally:
            self._cleanup()
    
    def _execute_query(self) -> None:
        """Execute the stored query with parameters."""
        if not self.query:
            raise ValueError("No query provided for execution")
            
        try:
            if self.parameters:
                logger.info(f"Executing query: {self.query} with parameters: {self.parameters}")
                self.cursor.execute(self.query, self.parameters)
            else:
                logger.info(f"Executing query: {self.query}")
                self.cursor.execute(self.query)
                
            # Store results for SELECT queries
            if self.query.strip().upper().startswith('SELECT'):
                self.results = self.cursor.fetchall()
                logger.info(f"Query executed successfully, returned {len(self.results)} rows")
            else:
                # For non-SELECT queries, store affected row count
                self.results = self.cursor.rowcount
                logger.info(f"Query executed successfully, affected {self.results} rows")
                
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def _cleanup(self) -> None:
        """Clean up database resources."""
        if self.cursor:
            self.cursor.close()
            logger.debug("Database cursor closed")
            
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute(self, query: str, parameters: tuple = None) -> 'ExecuteQuery':
        """
        Execute a new query within the same context.
        
        Args:
            query (str): SQL query to execute
            parameters (tuple): Parameters for the SQL query
            
        Returns:
            ExecuteQuery: self for method chaining
        """
        self.query = query
        self.parameters = parameters
        self._execute_query()
        return self
    
    def get_results(self) -> List[Tuple] | int:
        """
        Get the results of the executed query.
        
        Returns:
            List of tuples for SELECT queries, or int for affected rows
        """
        return self.results
    
    def get_column_names(self) -> List[str]:
        """
        Get column names from the executed query.
        
        Returns:
            List of column names
        """
        if self.cursor and self.cursor.description:
            return [description[0] for description in self.cursor.description]
        return []
    
    def get_first_result(self) -> Optional[Tuple]:
        """
        Get the first result from the query results.
        
        Returns:
            First row as tuple, or None if no results
        """
        if isinstance(self.results, list) and self.results:
            return self.results[0]
        return None
    
    def get_result_count(self) -> int:
        """
        Get the number of results returned by the query.
        
        Returns:
            Number of rows returned or affected
        """
        if isinstance(self.results, list):
            return len(self.results)
        return self.results if self.results else 0

# Enhanced version with additional features
class AdvancedExecuteQuery(ExecuteQuery):
    """
    Enhanced query execution context manager with additional features.
    """
    
    def __init__(self, db_path: str = 'users.db', query: str = None, parameters: tuple = None,
                 row_factory: Any = None, timeout: float = 30.0):
        """
        Initialize the advanced query executor.
        
        Args:
            row_factory: Row factory for custom row objects (e.g., sqlite3.Row)
            timeout (float): Timeout for database operations
        """
        super().__init__(db_path, query, parameters)
        self.row_factory = row_factory
        self.timeout = timeout
    
    def __enter__(self) -> 'AdvancedExecuteQuery':
        """Enter the context with enhanced features."""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=self.timeout
            )
            
            if self.row_factory:
                self.connection.row_factory = self.row_factory
                
            self.cursor = self.connection.cursor()
            logger.info(f"Advanced database connection opened: {self.db_path}")
            
            if self.query:
                self._execute_query()
                
            return self
            
        except sqlite3.Error as e:
            logger.error(f"Failed to open advanced database connection: {e}")
            self._cleanup()
            raise
    
    def get_results_as_dict(self) -> List[dict]:
        """
        Get results as a list of dictionaries.
        
        Returns:
            List of dictionaries where keys are column names
        """
        if not self.results or not isinstance(self.results, list):
            return []
            
        column_names = self.get_column_names()
        return [dict(zip(column_names, row)) for row in self.results]
    
    def execute_many(self, query: str, parameters_list: List[tuple]) -> 'AdvancedExecuteQuery':
        """
        Execute the same query multiple times with different parameters.
        
        Args:
            query (str): SQL query to execute
            parameters_list (List[tuple]): List of parameter tuples
            
        Returns:
            AdvancedExecuteQuery: self for method chaining
        """
        try:
            self.cursor.executemany(query, parameters_list)
            self.results = self.cursor.rowcount
            logger.info(f"Executed query {len(parameters_list)} times, affected {self.results} total rows")
            return self
        except sqlite3.Error as e:
            logger.error(f"Execute many failed: {e}")
            raise

# Example usage and demonstration
if __name__ == "__main__":
    print("=== Basic ExecuteQuery Usage ===")
    
    # Example 1: Basic usage with the specified query
    query = "SELECT * FROM users WHERE age > ?"
    parameters = (25,)
    
    with ExecuteQuery('users.db', query, parameters) as executor:
        results = executor.get_results()
        column_names = executor.get_column_names()
        
        print(f"Query: {query}")
        print(f"Parameters: {parameters}")
        print(f"Column names: {column_names}")
        print(f"Number of users over 25: {len(results)}")
        print("Results:")
        for row in results:
            print(row)
    
    print("\n=== Advanced ExecuteQuery Usage ===")
    
    # Example 2: Using the advanced version with dictionary results
    with AdvancedExecuteQuery(
        'users.db', 
        query, 
        parameters,
        row_factory=sqlite3.Row
    ) as advanced_executor:
        dict_results = advanced_executor.get_results_as_dict()
        
        print(f"Number of users over 25: {len(dict_results)}")
        print("Results as dictionaries:")
        for user_dict in dict_results:
            print(user_dict)
    
    print("\n=== Flexible Query Execution ===")
    
    # Example 3: Execute different queries in the same context
    with ExecuteQuery('users.db') as executor:
        # Execute first query
        executor.execute("SELECT COUNT(*) FROM users WHERE age > ?", (25,))
        count_over_25 = executor.get_first_result()[0]
        print(f"Users over 25: {count_over_25}")
        
        # Execute second query
        executor.execute("SELECT COUNT(*) FROM users WHERE age <= ?", (25,))
        count_under_25 = executor.get_first_result()[0]
        print(f"Users 25 or under: {count_under_25}")
        
        # Execute third query
        executor.execute("SELECT name, email FROM users WHERE age > ? ORDER BY name", (25,))
        users_over_25 = executor.get_results()
        print(f"Users over 25 (name and email):")
        for name, email in users_over_25:
            print(f"  {name}: {email}")
    
    print("\n=== Update Query Example ===")
    
    # Example 4: Execute an UPDATE query (commented out to avoid modifying data)
    # update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE age > ?"
    # with ExecuteQuery('users.db', update_query, (25,)) as executor:
    #     affected_rows = executor.get_results()
    #     print(f"Updated {affected_rows} user records")
    
    print("\n=== Error Handling Example ===")
    
    # Example 5: Error handling
    try:
        with ExecuteQuery('users.db', "SELECT * FROM nonexistent_table") as executor:
            results = executor.get_results()
    except sqlite3.OperationalError as e:
        print(f"Expected error handled: {e}")
