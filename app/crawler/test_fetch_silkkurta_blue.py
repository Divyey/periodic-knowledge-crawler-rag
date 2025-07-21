import os
from dotenv import load_dotenv

from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

# Import your local UUID conversion util
from app.utils.uuid_utils import get_uuid_from_chunk_id

# Set your target chunk_id and expected fields
TARGET_CHUNK_ID = "https://preprod-arunodayakurtis.zupain.com/SILKKURTA-(BLUE)/pd/d1cb7f77-92cd-404a-bc7c-273f9b81820e_chunk_0"
EXPECTED_HASH = "9bf9d84c12a01e828a2b38bde3c4b5ce8adaeec426089830d8e1e6c575a52fba"

def main():
    # Setup env and client
    load_dotenv()
    client = WeaviateClient(
        connection_params=ConnectionParams.from_params(
            http_host="localhost",
            http_port=8080,
            grpc_host="localhost",
            grpc_port=50051,
            http_secure=False,
            grpc_secure=False,
        )
    )
    client.connect()
    collection = client.collections.get("PageChunk")

    uuid = get_uuid_from_chunk_id(TARGET_CHUNK_ID)
    obj = collection.query.fetch_object_by_id(uuid)
    print("------ PRODUCT VERIFICATION ------")
    print("URL:       ", obj.properties.get("url") if obj else None)
    print("UUID:      ", uuid)
    print("Last hash: ", obj.properties.get("hash") if obj else None)
    print("Expected hash:", EXPECTED_HASH)
    print("Last updated:", obj.properties.get("last_updated") if obj else None)
    print("Current content (first 300 chars):\n")
    print(obj.properties.get("content", "")[:300] if obj else "None")

    if obj and obj.properties.get("hash") == EXPECTED_HASH:
        print("\n✅ SUCCESS: Hash matches expected. DB is up-to-date for the target chunk.")
    else:
        print("\n⚠️ WARNING: Hash mismatch or object not found! Check your upsert pipeline.")

    client.close()

if __name__ == "__main__":
    main()
