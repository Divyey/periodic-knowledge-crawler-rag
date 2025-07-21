from app.crawler.crawler_mp import main as crawl_main
from app.upsert.upsert import upsert_chunks_optimal

if __name__ == "__main__":
    chunks = crawl_main()
    print(f"Crawled {len(chunks)} chunks, starting upsert...")
    upsert_chunks_optimal(chunks)
    print("Full pipeline completed successfully.")
