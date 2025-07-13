
import contextlib
import seed   # assumes seed.py is in the same project folder


def stream_users():
    """
    Lazily yield each record as a dict, without loading the full result set.

    One `while` loop → fetches one row at a time; exits when `fetchone()` is None.
    """
    with contextlib.closing(seed.connect_to_prodev()) as conn, \
         contextlib.closing(conn.cursor(dictionary=True)) as cur:
        cur.execute("SELECT * FROM user_data")

        while True:                   
            row = cur.fetchone()
            if row is None:
                break
            yield row
