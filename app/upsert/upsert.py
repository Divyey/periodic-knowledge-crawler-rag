import os
import json
import traceback
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv

from openai import OpenAI
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

from app.utils.uuid_utils import get_uuid_from_chunk_id


# ==== Setup ====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client_ai = OpenAI(api_key=OPENAI_API_KEY)

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
SIMILARITY_THRESHOLD = 0.98


# ==== Helpers ====

def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def get_embedding(text: str) -> list:
    """Returns OpenAI embedding for a text chunk."""
    response = client_ai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


# ==== Main Upsert Logic ====

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
                # ✅ Fetch object from vector DB
                existing = collection.query.fetch_object_by_id(uuid)

                existing_hash = existing.properties.get("hash") if existing else None
                existing_vector = existing.vector if existing else None

                if existing_hash == new_hash:
                    print(f"[SKIP ✅] Hash match: {chunk_id}")
                    skipped += 1
                    continue

                new_vector = get_embedding(new_content)

                if existing_vector:
                    similarity = cosine_similarity(new_vector, existing_vector)
                    if similarity >= SIMILARITY_THRESHOLD:
                        print(f"[SKIP 🤖] Vector match: {chunk_id} (sim={similarity:.4f})")
                        skipped += 1
                        continue

                collection.data.replace(uuid=uuid, properties=properties)
                print(f"[REPLACE 🔄] {chunk_id}")
                replaced += 1

            else:
                # Not in DB yet
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


# ==== Entry Point ====

def main():
    path = "data/site_chunks.json"
    if not os.path.exists(path):
        print("❌ No site_chunks.json found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"\n🚀 Starting optimal upsert for {len(chunks)} chunks...\n")
    upsert_chunks_optimal(chunks)


if __name__ == "__main__":
    main()
