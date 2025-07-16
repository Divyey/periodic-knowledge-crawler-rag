import sys
import time
import json
from urllib.parse import urljoin, urlparse
import scrapy
from scrapy.crawler import CrawlerProcess
from common_utils import chunk_text, hash_chunk, print_stats

def extract_links(response, base_url):
    links = set()
    for href in response.css('a::attr(href)').getall():
        full_url = urljoin(base_url, href)
        if urlparse(full_url).scheme in ("http", "https"):
            links.add(full_url)
    return list(links)

class SimpleSpider(scrapy.Spider):
    name = "simplespider"
    custom_settings = {'LOG_ENABLED': False}
    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [url]
        self.base_url = url
        self.start_time = time.time()

    def parse(self, response):
        text = " ".join(response.xpath("//body//text()").getall())
        chunks = chunk_text(text)
        end = time.time()
        print_stats("Scrapy", self.start_time, end, chunks)
        links = extract_links(response, self.base_url)
        output = {
            "url": self.base_url,
            "chunks": chunks,
            "total_urls_found": len(links),
            "unique_urls": links
        }
        with open("scrapy_output.json", "w") as f:
            json.dump(output, f, indent=2)
        print("Saved output to scrapy_output.json")

def crawl_scrapy(url):
    process = CrawlerProcess()
    process.crawl(SimpleSpider, url=url)
    process.start()

if __name__ == "__main__":
    url = sys.argv[1]
    crawl_scrapy(url)
