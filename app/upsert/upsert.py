import os
import traceback
from tqdm import tqdm
from dotenv import load_dotenv

from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

from app.utils.uuid_utils import get_uuid_from_chunk_id

# ==== Setup ====
load_dotenv()

client_wv = WeaviateClient(
    connection_params=ConnectionParams.from_params(
        http_host="localhost",
        http_port=8080,
        grpc_host="localhost",
        grpc_port=50051,
        http_secure=False,
        grpc_secure=False
    )
)

collection_name = "PageChunk"

def upsert_chunks_optimal(chunks):
    try:
        client_wv.connect()
        collection = client_wv.collections.get(collection_name)
    except Exception as e:
        raise SystemExit(f"❌ Cannot connect to Weaviate or collection: {e}")

    inserted, replaced, skipped, failed = 0, 0, 0, 0

    for chunk in tqdm(chunks, desc="Upserting", unit="chunk"):
        chunk_id = chunk.get("chunk_id")
        uuid = get_uuid_from_chunk_id(chunk_id)
        new_hash = chunk.get("hash")
        new_content = chunk.get("content")

        properties = {
            "chunk_id": chunk["chunk_id"],
            "url": chunk["url"],
            "content": chunk["content"],
            "hash": chunk["hash"],
            "last_updated": chunk["last_updated"]
        }

        try:
            if collection.data.exists(uuid):
                # 🔍 Fetch object from vector DB
                existing = collection.query.fetch_object_by_id(uuid)
                existing_hash = existing.properties.get("hash") if existing else None

                if existing_hash == new_hash:
                    print(f"[SKIP ✅] Hash match: {chunk_id}")
                    skipped += 1
                    continue

                print(f"[REPLACE 🔄] {chunk_id}")
                print(f"⏪ Old hash: {existing_hash}")
                print(f"⏩ New hash: {new_hash}")
                collection.data.replace(uuid=uuid, properties=properties)

                # ✅ Verify from DB
                try:
                    updated = collection.query.fetch_object_by_id(uuid)
                    updated_content = updated.properties.get("content", "")
                    preview = updated_content.strip().replace("\n", " ")[:200]
                    print(f"🔁 [VERIFY] Content preview: {preview}...")
                except Exception as fetch_err:
                    print(f"⚠️ Fetch-after-replace failed: {fetch_err}")

                replaced += 1
            else:
                # ➕ New insert
                collection.data.insert(uuid=uuid, properties=properties)
                print(f"[INSERT ➕] {chunk_id}")
                inserted += 1

        except Exception as err:
            print(f"[FAILED ❌] {chunk_id} → {err}")
            traceback.print_exc()
            failed += 1

    print("\n📊 Upsert Summary:")
    print(f"🆕 Inserted : {inserted}")
    print(f"♻️  Replaced : {replaced}")
    print(f"⏭️  Skipped  : {skipped}")
    print(f"❌ Failed    : {failed}")
    print(f"📦 Total     : {len(chunks)}")

    client_wv.close()

def main(chunks=None):
    if chunks is None:
        path = "data/site_chunks.json"
        if not os.path.exists(path):
            print("❌ No site_chunks.json found.")
            return
        import json
        with open(path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    print(f"\n🚀 Starting optimal upsert for {len(chunks)} chunks...\n")
    upsert_chunks_optimal(chunks)

if __name__ == "__main__":
    main()
