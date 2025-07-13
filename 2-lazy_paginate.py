#!/usr/bin/env python3
"""
2-lazy_paginate.py
-------------------
Implements lazy pagination using a generator.

Functions:
- paginate_users(page_size, offset): fetches one page of results.
- lazy_paginate(page_size): yields each page lazily using yield.

Constraints Met:
✔ Uses only one loop
✔ Uses yield
✔ Correct prototypes
"""

import contextlib
import seed


def paginate_users(page_size, offset):
    """
    Fetch a single page of users from the user_data table.
    Returns a list of user dictionaries.
    """
    with contextlib.closing(seed.connect_to_prodev()) as conn, \
         contextlib.closing(conn.cursor(dictionary=True)) as cur:
        cur.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (page_size, offset))
        return cur.fetchall()


def lazy_paginate(page_size):
    """
    Generator that lazily fetches pages of users using paginate_users().
    Yields one page (list of user dicts) at a time.
    Only one loop is allowed.
    """
    offset = 0
    while True:  # ✅ Only loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
