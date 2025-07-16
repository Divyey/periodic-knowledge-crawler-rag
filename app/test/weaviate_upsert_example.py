# app/test/weaviate_upsert_example.py
import os
from dotenv import load_dotenv
import weaviate
from common_utils import hash_chunk

load_dotenv()

client = weaviate.Client(
    url=os.getenv("WEAVIATE_CLUSTER_URL"),
    auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
)

def upsert_chunks(chunks, url):
    for idx, chunk in enumerate(chunks):
        chunk_hash = hash_chunk(chunk)
        data_object = {
            "chunk_id": f"{url}_chunk_{idx}",
            "url": url,
            "content": chunk,
            "hash": chunk_hash
        }
        client.data_object.create(data_object, "PageChunk")
        print(f"Upserted chunk {idx} with hash {chunk_hash}")

# Example usage:
# from beautifulsoup_crawl import crawl_bs4
# chunks = crawl_bs4("https://your-url.com")
# upsert_chunks(chunks, "https://your-url.com")

