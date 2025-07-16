from app.crawler.crawler_mp import main as crawl_main
from app.upsert.upsert import main as upsert_main

if __name__ == "__main__":
    crawl_main()
    upsert_main()
