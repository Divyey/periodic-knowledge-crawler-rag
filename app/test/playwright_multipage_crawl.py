# app/test/playwright_multipage_crawl.py
import sys
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from common_utils import chunk_text, hash_chunk, print_stats

async def crawl_pages(base_url, page_param="page", max_pages=1000):
    all_chunks = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for i in range(1, max_pages+1):
            url = f"{base_url}?{page_param}={i}"
            await page.goto(url, wait_until="networkidle")
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
            all_chunks.extend(chunk_text(text))
        await browser.close()
    print_stats("Playwright Multi-page", 0, 0, all_chunks)  # You can time as before

if __name__ == "__main__":
    base_url = sys.argv[1]
    asyncio.run(crawl_pages(base_url))
