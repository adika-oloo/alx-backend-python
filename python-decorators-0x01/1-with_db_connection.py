import sqlite3
import functools
import mysql.connector  # You would need to install this: pip install mysql-connector-python

def with_db_connection(db_type='sqlite', **db_config):
    """
    Advanced decorator that supports multiple database types.
    
    Args:
        db_type (str): 'sqlite' or 'mysql'
        **db_config: Database configuration parameters
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            try:
                if db_type == 'sqlite':
                    db_path = db_config.get('db_path', 'users.db')
                    conn = sqlite3.connect(db_path)
                elif db_type == 'mysql':
                    conn = mysql.connector.connect(
                        host=db_config.get('host', 'localhost'),
                        user=db_config.get('user', 'root'),
                        password=db_config.get('password', ''),
                        database=db_config.get('database', 'test')
                    )
                else:
                    raise ValueError(f"Unsupported database type: {db_type}")
                
                # Call the function with the connection
                result = func(conn, *args, **kwargs)
                
                # Commit for SQLite (MySQL autocommit can be configured differently)
                if db_type == 'sqlite':
                    conn.commit()
                    
                return result
                
            except Exception as e:
                if conn:
                    conn.rollback()
                raise e
            finally:
                if conn:
                    conn.close()
                    
        return wrapper
    return decorator

# MySQL example (commented out as it requires MySQL setup)
# @with_db_connection(db_type='mysql', host='localhost', user='root', 
#                    password='password', database='myapp')
# def mysql_get_user(conn, user_id):
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
#     return cursor.fetchone()
