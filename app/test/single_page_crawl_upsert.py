import os
import sys
import weaviate
from dotenv import load_dotenv

# Add imports from your app modules
from app.embed.openai_embed import embed_openai_text
from app.upsert.upsert import upsert_chunks
from app.crawler.crawler_mp import scrape_url_with_selenium

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_CLUSTER_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
COLLECTION_NAME = os.getenv("WEAVIATE_COLLECTION", "PageChunk")

# ==== Connect to Weaviate ====
def get_client():
    return weaviate.connect_to_local()  # Or use connect_to_weaviate_cloud() if using cloud

# ==== Main ====
def main():
    if len(sys.argv) != 2:
        print("Usage: python single_page_crawl_upsert.py '<url>'")
        sys.exit(1)

    url = sys.argv[1]
    print(f"🔎 Fetching: {url}\n")

    chunks = scrape_url_with_selenium(url)

    if not chunks:
        print("⚠️ No content found — skipping upsert.")
        return

    client = get_client()
    collection = client.collections.get(COLLECTION_NAME)

    print(f"🧠 {len(chunks)} new chunk(s) scraped. Now saving with overwrite...")
    upsert_chunks(collection, chunks, embed_fn=embed_openai_text)

    print("✅ Done.")

if __name__ == "__main__":
    main()
