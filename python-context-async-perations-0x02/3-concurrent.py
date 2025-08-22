import time
from datetime import datetime

async def async_fetch_users_with_delay() -> List[Tuple]:
    """Fetch all users with a simulated delay"""
    start_time = time.time()
    async with aiosqlite.connect(":memory:") as db:
        # Simulate some processing time
        await asyncio.sleep(0.1)
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            end_time = time.time()
            print(f"Fetched {len(results)} users in {end_time-start_time:.3f}s")
            return results

async def async_fetch_older_users_with_delay() -> List[Tuple]:
    """Fetch older users with a simulated delay"""
    start_time = time.time()
    async with aiosqlite.connect(":memory:") as db:
        # Simulate some processing time
        await asyncio.sleep(0.1)
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            end_time = time.time()
            print(f"Fetched {len(results)} older users in {end_time-start_time:.3f}s")
            return results

async def demonstrate_concurrency():
    """Demonstrate the concurrency benefits"""
    print("Demonstrating concurrent execution...")
    
    # Sequential execution (for comparison)
    print("\nSequential execution:")
    start_seq = time.time()
    result1 = await async_fetch_users_with_delay()
    result2 = await async_fetch_older_users_with_delay()
    end_seq = time.time()
    print(f"Sequential total time: {end_seq-start_seq:.3f}s")
    
    # Concurrent execution
    print("\nConcurrent execution:")
    start_conc = time.time()
    result1, result2 = await asyncio.gather(
        async_fetch_users_with_delay(),
        async_fetch_older_users_with_delay()
    )
    end_conc = time.time()
    print(f"Concurrent total time: {end_conc-start_conc:.3f}s")
    print(f"Time saved: {((end_seq-start_seq) - (end_conc-start_conc)):.3f}s")
