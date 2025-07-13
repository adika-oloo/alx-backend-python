#!/usr/bin/env python3
"""
1-batch_processing.py
---------------------
Two generator-based functions:

- stream_users_in_batches(batch_size): yields users from DB in batches
- batch_processing(batch_size): filters users over age 25 from each batch

Constraints met:
- Uses `yield`
- Uses no more than 3 loops total
"""

import contextlib
import seed  # assumes seed.py provides connect_to_prodev()


def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of users from the database.
    Each yield returns a list of user dicts.
    """
    offset = 0

    while True:  # loop #1
        with contextlib.closing(seed.connect_to_prodev()) as conn, \
             contextlib.closing(conn.cursor(dictionary=True)) as cur:
            cur.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (batch_size, offset))
            rows = cur.fetchall()
            if not rows:
                break
            yield rows
            offset += batch_size


def batch_processing(batch_size):
    """
    Processes batches by filtering users older than 25 years.
    Prints each matching user dictionary.
    """
    for batch in stream_users_in_batches(batch_size):  # loop #2
        for user in batch:  # loop #3
            if user["age"] > 25:
                print(user)
