import time
import sqlite3 
import functools
import random
import logging
from typing import Tuple, Type

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def with_db_connection(db_path='users.db', timeout=30):
    """Enhanced connection decorator with timeout support."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db_path, timeout=timeout)
            try:
                logger.info(f"Connected to database: {db_path}")
                result = func(conn, *args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Database error: {e}")
                raise e
            finally:
                conn.close()
                logger.info("Database connection closed")
        return wrapper
    return decorator

def retry_on_failure(
    retries: int = 3, 
    delay: float = 2, 
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    """
    Advanced retry decorator with exponential backoff and configurable exceptions.
    
    Args:
        retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        exceptions: Tuple of exception types to catch and retry on
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        jitter: Whether to add random jitter to avoid synchronized retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(
                            f"Retry {attempt}/{retries} for {func.__name__} "
                            f"after {current_delay:.2f}s"
                        )
                        time.sleep(current_delay)
                    
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Log success after retries
                    if attempt > 0:
                        logger.info(f"Success on retry {attempt} for {func.__name__}")
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt < retries:
                        # Log the retryable error
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}"
                        )
                        
                        # Calculate next delay with exponential backoff
                        current_delay = min(current_delay * backoff_factor, max_delay)
                        
                        # Add jitter to avoid synchronized retries
                        if jitter:
                            jitter_amount = current_delay * 0.1 * random.random()
                            current_delay += jitter_amount
                    else:
                        # Final failure
                        logger.error(
                            f"All {retries + 1} attempts failed for {func.__name__}. "
                            f"Last error: {last_exception}"
                        )
                        raise last_exception
            
            raise last_exception  # Should never reach here
        return wrapper
    return decorator

# Common transient database errors (SQLite specific)
TRANSIENT_ERRORS = (sqlite3.OperationalError, sqlite3.DatabaseError)

# Usage examples:

@with_db_connection
@retry_on_failure(
    retries=3, 
    delay=1, 
    exceptions=TRANSIENT_ERRORS,
    backoff_factor=1.5
)
def fetch_users_with_retry(conn):
    """Fetch all users with retry on transient errors."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    logger.info(f"Fetched {len(results)} users")
    return results

@with_db_connection
@retry_on_failure(
    retries=5,
    delay=0.5,
    exceptions=(sqlite3.OperationalError,),
    backoff_factor=2.0,
    max_delay=10.0
)
def update_user_with_retry(conn, user_id, new_email):
    """Update user email with aggressive retry strategy."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?", 
        (new_email, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    logger.info(f"Updated {affected} user(s)")
    return affected

@with_db_connection
@retry_on_failure(
    retries=2,
    delay=2,
    exceptions=(sqlite3.OperationalError, sqlite3.IntegrityError)
)
def complex_operation_with_retry(conn):
    """Example of a complex operation with retry logic."""
    cursor = conn.cursor()
    
    # Multiple operations in a transaction
    cursor.execute("INSERT INTO audit_log (action) VALUES ('batch_process')")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    # Simulate a potential transient error
    if random.random() < 0.3:  # 30% chance to simulate error
        raise sqlite3.OperationalError("Simulated database lock")
    
    conn.commit()
    return user_count

# Test function that simulates transient failures
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def unreliable_operation(conn):
    """Operation that fails randomly to demonstrate retry logic."""
    cursor = conn.cursor()
    
    # Simulate random failures (50% chance)
    if random.random() < 0.5:
        raise sqlite3.OperationalError("Random database timeout")
    
    cursor.execute("SELECT 1")
    return cursor.fetchone()

if __name__ == "__main__":
    try:
        # Test basic retry functionality
        users = fetch_users_with_retry()
        print(f"Successfully fetched {len(users)} users")
        
        # Test update operation
        updated = update_user_with_retry(user_id=1, new_email='new@example.com')
        print(f"Updated {updated} row(s)")
        
        # Test complex operation
        count = complex_operation_with_retry()
        print(f"Complex operation completed. User count: {count}")
        
        # Test unreliable operation (will show retries in action)
        result = unreliable_operation()
        print(f"Unreliable operation succeeded: {result}")
        
    except Exception as e:
        print(f"Final failure: {e}")
