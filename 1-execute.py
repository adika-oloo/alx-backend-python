#!/usr/bin/env python3
"""
1-execute_query.py
------------------
Reusable context‑manager ExecuteQuery that:

• opens a MySQL connection
• executes the supplied statement with parameters
• returns the fetched rows from __enter__
• always closes cursor & connection in __exit__

Example use:

    db_cfg = {"host": "localhost", "user": "root",
              "password": "secret", "database": "ALX_prodev"}

    with ExecuteQuery(
            "SELECT * FROM users WHERE age > %s", (25,),
            **db_cfg) as rows:
        for r in rows:
            print(r)
"""

import mysql.connector
from mysql.connector import Error


class ExecuteQuery:
    """Context manager that executes a parametrized query and returns rows."""

    def __init__(self, query: str, params: tuple | None = None, **db_cfg):
        self.query = query
        self.params = params or ()
        self.db_cfg = db_cfg
        self.conn = None
        self.cursor = None
        self.rows = None

    # --------------------------------------------------------------------- #
    # Context‑manager protocol
    # --------------------------------------------------------------------- #
    def __enter__(self):
        """Open connection, run query, fetch rows, and return them."""
        self.conn = mysql.connector.connect(**self.db_cfg)
        self.cursor = self.conn.cursor(dictionary=True)
        self.cursor.execute(self.query, self.params)
        self.rows = self.cursor.fetchall()   # grab data before closing
        return self.rows                     # ← what 'with' assigns

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure cleanup. Propagate exceptions (return False)."""
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None and self.conn.is_connected():
            self.conn.close()
        # Returning False ⇒ any exception propagates
        return False


# ------------------------------------------------------------------------- #
# Quick demo when file is run directly
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "root",      
        "database": "ALX_prodev",
        "charset": "utf8mb4",
    }

    try:
        with ExecuteQuery(
            "SELECT * FROM users WHERE age > %s", (25,), **CONFIG
        ) as results:
            for row in results:
                print(row)
    except Error as err:
        print(f"MySQL error: {err}")
