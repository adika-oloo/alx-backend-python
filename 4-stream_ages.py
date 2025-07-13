#!/usr/bin/env python3
"""
4-stream_ages.py
-----------------
Use a generator to stream user ages and calculate average age efficiently.

Requirements met:
✔ Uses `yield`
✔ ≤ 2 loops total
✔ No SQL AVERAGE used
✔ Streams rows one-by-one (memory efficient)
"""

import contextlib
import seed


def stream_user_ages():
    """
    Generator that yields each user's age one by one.
    Fetches using cursor with dictionary=True.
    """
    with contextlib.closing(seed.connect_to_prodev()) as conn, \
         contextlib.closing(conn.cursor(dictionary=True)) as cur:
        cur.execute("SELECT age FROM user_data")
        while True:  # loop #1
            row = cur.fetchone()
            if not row:
                break
            yield row["age"]


def calculate_average_age():
    """
    Consumes stream_user_ages() to calculate and print average age.
    Avoids loading all rows into memory.
    """
    total_age = 0
    count = 0
    for age in stream_user_ages():  # loop #2
        total_age += float(age)
        count += 1

    if count > 0:
        average = total_age / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found.")
