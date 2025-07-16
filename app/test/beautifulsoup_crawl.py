import sys
import time
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from common_utils import chunk_text, hash_chunk, print_stats

def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if urlparse(href).scheme in ("http", "https"):
            links.add(href)
    return list(links)

def crawl_bs4(url):
    start = time.time()
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    chunks = chunk_text(text)
    end = time.time()
    print_stats("BeautifulSoup", start, end, chunks)
    links = extract_links(soup, url)
    output = {
        "url": url,
        "chunks": chunks,
        "total_urls_found": len(links),
        "unique_urls": links
    }
    with open("beautifulsoup_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Saved output to beautifulsoup_output.json")

if __name__ == "__main__":
    url = sys.argv[1]
    crawl_bs4(url)
