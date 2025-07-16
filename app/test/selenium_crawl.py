import sys
import time
import json
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from common_utils import chunk_text, hash_chunk, print_stats

def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if urlparse(href).scheme in ("http", "https"):
            links.add(href)
    return list(links)

def crawl_selenium(url):
    start = time.time()
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)  # Wait for JS to load
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    chunks = chunk_text(text)
    end = time.time()
    print_stats("Selenium", start, end, chunks)
    links = extract_links(soup, url)
    output = {
        "url": url,
        "chunks": chunks,
        "total_urls_found": len(links),
        "unique_urls": links
    }
    with open("selenium_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Saved output to selenium_output.json")

if __name__ == "__main__":
    url = sys.argv[1]
    crawl_selenium(url)
