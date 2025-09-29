#!/usr/bin/python3
"""
Memory-Efficient Aggregation with Generators
Computes the average age of users without loading all rows into memory
"""

seed = __import__('seed')


def stream_user_ages():
    """
    Generator that streams user ages one by one from the database
    Yields:
        int: age of each user
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:  # loop 1
        yield row['age']

    connection.close()


def compute_average_age():
    """
    Consumes the generator to compute average age in a memory-efficient way
    """
    total = 0
    count = 0

    for age in stream_user_ages():  # loop 2
        total += age
        count += 1

    if count > 0:
        avg = total / count
        print(f"Average age of users: {avg:.2f}")
    else:
        print("No users found.")


if __name__ == "__main__":
    compute_average_age()
