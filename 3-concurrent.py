#!/usr/bin/env python3
"""
2-concurrent_queries.py
-----------------------
Run two SQLite queries concurrently using asyncio.gather + aiosqlite.

• async_fetch_users()        -> fetches every row from users table
• async_fetch_older_users()  -> fetches users where age > 40
• fetch_concurrently()       -> runs both in parallel and prints results
"""

import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "users.db"


async def async_fetch_users():
    """Return a list of all users."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cur:
            return await cur.fetchall()


async def async_fetch_older_users():
    """Return users older than 40."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cur:
            return await cur.fetchall()


async def fetch_concurrently():
    """Run both queries at once and print the results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(), async_fetch_older_users()
    )

    print("=== All users ===")
    for row in all_users:
        print(dict(row))

    print("\n=== Users older than 40 ===")
    for row in older_users:
        print(dict(row))


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
