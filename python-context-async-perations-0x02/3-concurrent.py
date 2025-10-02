import asyncio
import aiosqlite

# Asynchronous function to fetch all users
async def async_fetch_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All users fetched:")
            for row in results:
                print(row)
            return results

# Asynchronous function to fetch users older than 40
async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            results = await cursor.fetchall()
            print("Users over 40 fetched:")
            for row in results:
                print(row)
            return results

# Function to execute both queries concurrently using asyncio.gather
async def fetch_concurrently():
    # Execute both functions concurrently and gather their results
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return results

# Run the concurrent fetch
if __name__ == "__main__":
    # Execute the async workflow
    all_results = asyncio.run(fetch_concurrently())
    print("Concurrent fetching completed!")
    print(f"Results: {all_results}")
