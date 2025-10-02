import sqlite3
import functools
import time
from datetime import datetime

def log_queries(verbose=False):
    """
    Decorator that logs SQL queries with optional verbose mode.
    
    Args:
        verbose (bool): If True, shows execution time and result count
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query from arguments
            query = None
            if 'query' in kwargs:
                query = kwargs['query']
            elif args and isinstance(args[0], str):
                query = args[0]
            
            if query:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Executing query: {query}")
                
                if verbose:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    result_count = len(result) if isinstance(result, (list, tuple)) else "N/A"
                    
                    print(f"[{timestamp}] Query completed in {execution_time:.2f}ms, returned {result_count} rows")
                    return result
                else:
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage examples:

# Basic usage
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Verbose usage with timing
@log_queries(verbose=True)
def fetch_users_with_details(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Test the decorators
if __name__ == "__main__":
    # Basic logging
    users = fetch_all_users(query="SELECT * FROM users")
    
    # Verbose logging with timing
    active_users = fetch_users_with_details(query="SELECT * FROM users WHERE active = 1")
    
    # Using positional argument
    all_data = fetch_all_users("SELECT * FROM sqlite_master")
