#!/usr/bin/python3
"""
Lazy loading paginated data from user_data table
"""

seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetch a page of users with given limit and offset
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily loads user pages from the database
    Args:
        page_size (int): Number of users per page
    Yields:
        list: A list of user records for each page
    """
    offset = 0
    while True:   # <-- only one loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
