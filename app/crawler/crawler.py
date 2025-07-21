# this is a "test crawler" with beautifulsoup and playwright to crawl a site and extract text and links
import os
import sys
import time
import json
import asyncio
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
from app.utils.hash_utils import compute_hash

START_URL = "https://preprod-arunodayakurtis.zupain.com/product-list"
DOMAIN = "preprod-arunodayakurtis.zupain.com"
MAX_PAGES = 10
CONCURRENCY = 16

SKIP_PATTERNS = [
    "/login", "/sign-up", "/bag", "/document/[path]", "/[path]/pd/[...pd]", "/explore"
]

def is_valid(link, visited, to_visit):
    return (
        link not in visited and
        link not in to_visit and
        "[" not in link and
        "]" not in link and
        not any(skip in link for skip in SKIP_PATTERNS)
        and not link.rstrip("/").endswith(DOMAIN)
    )

async def extract_links_and_text(page, url):
    async def block_resource(route):
        if route.request.resource_type in ["image", "stylesheet", "font"]:
            await route.abort()
        else:
            await route.continue_()
    await page.route("**/*", block_resource)
    await page.goto(url, wait_until="networkidle", timeout=60000)
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == DOMAIN and parsed.scheme in ("http", "https"):
            links.add(href.split("#")[0])
    return text, links

async def worker(queue, visited, all_chunks, all_found_urls, pbar, chunk_size, browser):
    while True:
        url = await queue.get()
        try:
            if url is None:
                print(f"[Worker] Received stop signal.")
                break
            if url in visited:
                continue
            context = await browser.new_context()
            page = await context.new_page()
            try:
                print(f"[Worker] Crawling: {url}")
                start_time = time.time()
                text, links = await extract_links_and_text(page, url)
                elapsed = time.time() - start_time
                print(f"[Worker] Done: {url} ({elapsed:.1f}s, {len(links)} links found)")
            except Exception as e:
                print(f"[Worker] ERROR: {url} ({type(e).__name__}): {e}")
            else:
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i+chunk_size]
                    if chunk.strip():
                        chunk_id = f"{url}_chunk_{i//chunk_size}"
                        all_chunks.append({
                            "chunk_id": chunk_id,
                            "url": url,
                            "content": chunk,
                            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "hash": compute_hash(chunk)
                        })
                for link in links:
                    all_found_urls.add(link)
                    if is_valid(link, visited, queue._queue):
                        await queue.put(link)
                visited.add(url)
                pbar.update(1)
            await page.close()
            await context.close()
        finally:
            queue.task_done()

async def crawl_site(start_url):
    visited = set()
    all_chunks = []
    all_found_urls = set()
    chunk_size = 500

    queue = asyncio.Queue()
    await queue.put(start_url)

    pbar = tqdm(total=MAX_PAGES, desc="Crawling", unit="page")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            workers = [
                asyncio.create_task(worker(queue, visited, all_chunks, all_found_urls, pbar, chunk_size, browser))
                for _ in range(CONCURRENCY)
            ]

            idle_seconds = 0
            last_visited = 0
            try:
                while len(visited) < MAX_PAGES:
                    if queue.empty():
                        if last_visited == len(visited):
                            idle_seconds += 1
                        else:
                            idle_seconds = 0
                            last_visited = len(visited)
                        if idle_seconds > 30:
                            print("[Main] No new URLs for 30s. Exiting early.")
                            break
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                print("\n[Main] KeyboardInterrupt received! Saving progress and shutting down...")
            finally:
                # Send stop signal to all workers and wait for them to finish
                for _ in workers:
                    await queue.put(None)
                await queue.join()
                for w in workers:
                    await w
                await browser.close()
            pbar.close()
    finally:
        print(f"[Main] Finished. Crawled {len(visited)} pages.")
        print(f"[Main] About to save {len(all_chunks)} chunks to data/site_chunks.json")
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/site_chunks.json", "w") as f:
                json.dump(all_chunks, f, indent=2)
            with open("data/unique_urls.json", "w") as f:
                json.dump(sorted(list(visited)), f, indent=2)
            with open("data/all_found_urls.json", "w") as f:
                json.dump(sorted(list(all_found_urls)), f, indent=2)
            print(f"[Main] Saved {len(all_chunks)} chunks, {len(visited)} unique visited URLs, {len(all_found_urls)} found URLs.")
        except Exception as e:
            print(f"[Main] ERROR saving files: {e}")

def main():
    asyncio.run(crawl_site(START_URL))

if __name__ == "__main__":
    main()
