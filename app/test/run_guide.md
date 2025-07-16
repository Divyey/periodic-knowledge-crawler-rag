1. Playwright (Async, JS-rendered, Fast)

bash
python app/test/playwright_crawl.py "https://your-url.com"


2. Selenium (Sync, JS-rendered)

bash
python app/test/selenium_crawl.py "https://your-url.com"

3. Scrapy (Async, Fast, Best for Static/HTML)

bash
python app/test/scrapy_crawl.py "https://your-url.com"


4. BeautifulSoup (Sync, HTTP Only)

bash
python app/test/beautifulsoup_crawl.py "https://your-url.com"

5. Run the parallel benchmark: 

bash
python app/test/parallel_benchmark.py "https://your-url.com"

6. Try multi-page crawling:

bash
python app/test/parallel_benchmark.py "https://preprod-arunodayakurtis.zupain.com/product-list"
