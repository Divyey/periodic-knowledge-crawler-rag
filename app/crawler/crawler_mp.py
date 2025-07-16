import os
import sys
import time
import json
import asyncio
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from app.crawler.sitemap import extract_sitemap_links
from app.crawler.robots import is_allowed
from app.utils.hash_utils import compute_hash

# ENV variables
START_URL = os.getenv("CRAWLER_START_URL", "https://preprod-arunodayakurtis.zupain.com")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
WAIT_SECONDS = float(os.getenv("CRAWLER_WAIT_SECONDS", 2))
CONCURRENCY = int(os.getenv("CRAWLER_CONCURRENCY", 8))  # Reduced concurrency for stability

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-zygote")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-crash-reporter")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_url_with_selenium(url, chunk_size=CHUNK_SIZE):
    body_text = ""
    chunks = []

    try:
        driver = get_driver()
        driver.get(url)

        try:
            # Wait for price symbol or Add to Cart (JS-loaded content)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//*[contains(text(), '₹') or contains(text(), 'Add to Cart')]"
                ))
            )
        except Exception as e:
            print(f"[WAIT TIMEOUT] {url}: {e}")

        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            print(f"[BODY ERROR] {url}: {e}")

    except Exception as e:
        print(f"[SCRAPE ERROR] {url}: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    if not body_text.strip():
        print(f"[EMPTY PAGE WARNING] No content extracted from: {url}")
        try:
            os.makedirs("logs/failures", exist_ok=True)
            with open(f"logs/failures/{url.split('/')[-1]}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception as e:
            print(f"[SNAPSHOT ERROR] Could not log failed page HTML for {url}: {e}")

    # Chunk the page content
    for i in range(0, len(body_text), chunk_size):
        chunk = body_text[i:i + chunk_size]
        if chunk.strip():
            content_hash = compute_hash(chunk)
            chunks.append({
                "url": url,
                "content": chunk,
                "chunk_id": f"{url}_chunk_{i // chunk_size}",
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "hash": content_hash
            })

    return chunks

async def get_crawlable_urls(site_url):
    all_urls = await extract_sitemap_links(site_url)
    print(f"[SITEMAP] Total URLs collected: {len(all_urls)}")
    os.makedirs("data", exist_ok=True)

    with open("data/all_urls.json", "w") as f:
        json.dump(sorted(list(all_urls)), f, indent=2)

    crawlable = [u for u in all_urls if is_allowed(u)]
    print(f"Total crawlable URLs (after robots.txt): {len(crawlable)}")

    with open("data/crawlable_urls.json", "w") as f:
        json.dump(sorted(list(crawlable)), f, indent=2)

    return crawlable

async def crawl_all_sitemap_urls(site_url, chunk_size=CHUNK_SIZE, concurrency=CONCURRENCY):
    urls = await get_crawlable_urls(site_url)
    all_chunks = []
    visited = []
    pbar = tqdm(total=len(urls), desc="Crawling", unit="page", dynamic_ncols=True)
    sem = asyncio.Semaphore(concurrency)

    async def crawl_one(url):
        async with sem:
            try:
                chunks = await asyncio.to_thread(scrape_url_with_selenium, url, chunk_size)
                if not chunks:
                    print(f"[RETRY] Retrying crawl for: {url}")
                    chunks = await asyncio.to_thread(scrape_url_with_selenium, url, chunk_size)
            except Exception as e:
                print(f"[CRAWL ERROR] {url}: {e}")
                chunks = []

            all_chunks.extend(chunks)
            visited.append(url)
            pbar.set_postfix({
                "Done": len(visited),
                "Remain": pbar.total - len(visited),
                "ETA": pbar.format_interval(
                    pbar.format_dict['elapsed'] *
                    (pbar.total - len(visited)) /
                    max(1, len(visited))
                )
            })
            pbar.update(1)

    tasks = [crawl_one(url) for url in urls]
    await asyncio.gather(*tasks)

    pbar.close()

    with open("data/visited_urls.json", "w") as f:
        json.dump(sorted(list(visited)), f, indent=2)

    return all_chunks

def main():
    os.makedirs("data", exist_ok=True)
    try:
        all_chunks = asyncio.run(crawl_all_sitemap_urls(START_URL))
        with open("data/site_chunks.json", "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2)

        print(f"\n[CRAWLER] Saved {len(all_chunks)} chunks to data/site_chunks.json")
    except KeyboardInterrupt:
        print("\n[CRAWLER] Interrupted manually. Exiting.")
    except Exception as e:
        print(f"[CRAWLER ERROR] {e}")

if __name__ == "__main__":
    main()

# # # grep -A 10 "SILKKURTA(BLUE-)" data/site_chunks.json
