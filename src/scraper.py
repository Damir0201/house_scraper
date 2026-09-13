import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def scrape_house_of_tracks():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()
        await page.goto("https://houseoftracks.com/tracks", wait_until="domcontentloaded")

        try:
            await page.wait_for_selector('text=€', timeout=12000)
        except Exception:
            print("Warning: price elements not found, parsing current DOM...")

        html_content = await page.content()
        await browser.close()

        soup = BeautifulSoup(html_content, "html.parser")
        tracks = []

        seen_urls = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not any(sub in href for sub in ["/track/", "/ghost-production/"]) and len(href.split('/')) < 3:
                continue

            parent_row = a_tag.find_parent("div")
            if not parent_row:
                continue

            price_elem = parent_row.find(string=lambda t: t and "€" in t)
            if not price_elem:
                continue

            track_url = href if href.startswith("http") else "https://houseoftracks.com" + href
            if track_url in seen_urls:
                continue
            seen_urls.add(track_url)

            title = a_tag.get_text(strip=True)
            if not title or len(title) < 2:
                continue

            tracks.append({
                "title": title,
                "genre": "Electronic",
                "price": price_elem.strip(),
                "track_url": track_url,
            })

        hot_picks = tracks[:6] if len(tracks) >= 6 else tracks
        catalog_tracks = tracks[6:] if len(tracks) > 6 else []

        return {
            "hot_picks": hot_picks,
            "catalog": catalog_tracks
        }


if __name__ == "__main__":
    data = asyncio.run(scrape_house_of_tracks())
    hot_picks = data.get("hot_picks", [])
    catalog = data.get("catalog", [])

    print(f"HoT Picks collected: {len(hot_picks)}")
    for t in hot_picks:
        print(f"Hot picks: {t}")

    print(f"\nCatalog tracks collected: {len(catalog)}")
    for t in catalog:
        print(f"New_tracks: {t}")