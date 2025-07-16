import sys
import asyncio
import time
import json
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from common_utils import chunk_text, hash_chunk, print_stats

def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if urlparse(href).scheme in ("http", "https"):
            links.add(href)
    return list(links)

async def crawl_playwright(url):
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    chunks = chunk_text(text)
    end = time.time()
    print_stats("Playwright", start, end, chunks)
    links = extract_links(soup, url)
    output = {
        "url": url,
        "chunks": chunks,
        "total_urls_found": len(links),
        "unique_urls": links
    }
    with open("playwright_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Saved output to playwright_output.json")

if __name__ == "__main__":
    url = sys.argv[1]
    asyncio.run(crawl_playwright(url))
