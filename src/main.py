import asyncio
from src.database import init_db, save_new_tracks
from src.scraper import scrape_house_of_tracks
from src.bot import send_broadcast_notifications


async def main():
    print("1. DB initializing...")
    init_db()

    print("2. Running parser House of Tracks...")
    scraped_data = await scrape_house_of_tracks()

    hot_picks = scraped_data.get("hot_picks", [])
    catalog = scraped_data.get("catalog", [])

    print("3. Saving to PostgreSQL...")
    new_hot_picks = save_new_tracks(hot_picks)
    new_catalog_tracks = save_new_tracks(catalog)

    print(f"New HoT Picks: {len(new_hot_picks)}, New in catalog: {len(new_catalog_tracks)}")

    print("4. Sending notifications...")
    await send_broadcast_notifications(new_hot_picks, new_catalog_tracks)
    print("all sent")


if __name__ == "__main__":
    asyncio.run(main())