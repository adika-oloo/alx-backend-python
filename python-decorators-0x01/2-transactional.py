import sqlite3 
import functools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def with_db_connection(db_path='users.db', autocommit=False):
    """
    Decorator that automatically handles database connections.
    
    Args:
        db_path (str): Path to the database file
        autocommit (bool): Whether to enable autocommit mode
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db_path)
            
            # Set autocommit if requested
            if autocommit:
                conn.isolation_level = None
                
            try:
                logger.info(f"Database connection opened to {db_path}")
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

def transactional(readonly=False):
    """
    Decorator that automatically handles database transactions.
    
    Args:
        readonly (bool): If True, no commit is performed (for read-only operations)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(conn, *args, **kwargs):
            # For read-only operations, we don't need transaction management
            if readonly:
                return func(conn, *args, **kwargs)
                
            try:
                logger.info("Starting database transaction")
                result = func(conn, *args, **kwargs)
                conn.commit()
                logger.info("Transaction committed successfully")
                return result
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise e
        return wrapper
    return decorator

# Usage examples:

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    affected_rows = cursor.rowcount
    if affected_rows == 0:
        raise ValueError(f"User with ID {user_id} not found")
    logger.info(f"Updated email for user {user_id} to {new_email}")
    return affected_rows

@with_db_connection 
@transactional 
def transfer_balance(conn, from_user_id, to_user_id, amount):
    """Example of a transaction with multiple operations"""
    cursor = conn.cursor()
    
    # Check if from_user has sufficient balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (from_user_id,))
    from_balance = cursor.fetchone()[0]
    
    if from_balance < amount:
        raise ValueError(f"Insufficient balance: {from_balance} < {amount}")
    
    # Deduct from sender
    cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", 
                   (amount, from_user_id))
    
    # Add to receiver
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", 
                   (amount, to_user_id))
    
    logger.info(f"Transferred {amount} from user {from_user_id} to user {to_user_id}")
    return amount

@with_db_connection 
@transactional(readonly=True)
def get_user_profile(conn, user_id):
    """Read-only operation - no transaction needed"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    return user

# Test the functions
if __name__ == "__main__":
    try:
        # Update user email with transaction
        result = update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print(f"Update successful: {result} row(s) affected")
        
        # Example of a failed transaction (will rollback)
        try:
            update_user_email(user_id=999, new_email='nonexistent@example.com')
        except ValueError as e:
            print(f"Expected error: {e}")
            
        # Read-only operation
        user = get_user_profile(user_id=1)
        print(f"User profile: {user}")
        
    except Exception as e:
        print(f"Operation failed: {e}")
