import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def scrape_house_of_tracks():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
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

        print("Http request")
        await page.goto("https://houseoftracks.com/tracks", wait_until="domcontentloaded")

        try:
            # Ждем появления элементов со ссылками на треки вместо слепого таймера
            await page.wait_for_selector('a[href*="/ghost-production/"]', timeout=10000)
        except Exception:
            print("Warning: selector haven't waited cards, trying something new...")

        html_content = await page.content()
        await browser.close()

        soup = BeautifulSoup(html_content, "html.parser")
        tracks = []

        cards = [
            a.parent.parent
            for a in soup.find_all("a", href=True)
            if "/ghost-production/" in a["href"]
        ]

        seen_urls = set()
        for card in cards:
            try:
                link_elem = card.find("a", href=lambda h: h and "/ghost-production/" in h)
                if not link_elem:
                    continue

                href = link_elem["href"]
                track_url = (
                    href if href.startswith("http") else "https://houseoftracks.com" + href
                )

                if track_url in seen_urls:
                    continue
                seen_urls.add(track_url)

                title = link_elem.get_text(strip=True)
                if not title or len(title) < 2:
                    title_elem = card.find(["h3", "h4", "span"])
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown"

                price_elem = card.find(string=lambda t: t and "€" in t)
                price = price_elem.strip() if price_elem else "0"

                if title != "Unknown":
                    tracks.append({
                        "title": title,
                        "genre": "Electronic",
                        "price": price,
                        "track_url": track_url,
                    })
            except Exception:
                continue

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