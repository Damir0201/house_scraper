import asyncio
from main import main


async def background_loop():
    print("Scheduler running")
    while True:
        try:
            print("release check")
            await main()
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(7200)


if __name__ == "__main__":
    asyncio.run(background_loop())