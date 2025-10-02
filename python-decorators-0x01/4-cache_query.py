import time
import sqlite3 
import functools
import hashlib
import pickle

query_cache = {}

def cache_query(max_size=100, ttl=None):
    """
    Decorator that caches the results of database queries to avoid redundant calls.
    
    Args:
        max_size (int): Maximum number of queries to cache (LRU eviction)
        ttl (float): Time-to-live in seconds for cache entries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            cache_key_data = {
                'func_name': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            
            # Use hash for efficient key storage
            cache_key = hashlib.md5(
                pickle.dumps(cache_key_data, pickle.HIGHEST_PROTOCOL)
            ).hexdigest()
            
            # Check if result is in cache and still valid
            current_time = time.time()
            if cache_key in query_cache:
                cached_data = query_cache[cache_key]
                
                # Check TTL if set
                if ttl is None or (current_time - cached_data['timestamp']) <= ttl:
                    print(f"Cache HIT for query: {kwargs.get('query', 'Unknown')}")
                    return cached_data['result']
                else:
                    # Remove expired entry
                    del query_cache[cache_key]
                    print(f"Cache EXPIRED for query: {kwargs.get('query', 'Unknown')}")
            
            # If not in cache or expired, execute the query
            print(f"Cache MISS for query: {kwargs.get('query', 'Unknown')}")
            result = func(*args, **kwargs)
            
            # Store result in cache
            query_cache[cache_key] = {
                'result': result,
                'timestamp': current_time,
                'query': kwargs.get('query', 'Unknown')
            }
            
            # Implement LRU eviction if cache exceeds max_size
            if len(query_cache) > max_size:
                # Remove oldest entry (first inserted)
                oldest_key = next(iter(query_cache))
                del query_cache[oldest_key]
                print(f"Cache evicted oldest entry (max_size: {max_size})")
            
            return result
        return wrapper
    return decorator

def with_db_connection(db_path='users.db'):
    """Decorator that automatically handles database connections."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db_path)
            try:
                result = func(conn, *args, **kwargs)
                return result
            except Exception as e:
                raise e
            finally:
                conn.close()
        return wrapper
    return decorator

@with_db_connection
@cache_query(max_size=50, ttl=300)  # Cache for 5 minutes, max 50 entries
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
