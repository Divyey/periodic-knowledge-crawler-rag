from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams
from tqdm import tqdm

COLLECTION_NAME = "PageChunk"

def wipe_all_objects():
    client = WeaviateClient(
        connection_params=ConnectionParams.from_params(
            http_host="localhost",
            http_port=8080,
            grpc_host="localhost",
            grpc_port=50051,
            http_secure=False,
            grpc_secure=False
        )
    )

    try:
        client.connect()
        print("✅ Connected to Weaviate")

        collections = client.collections.list_all()
        print(f"🎯 Available collections: {collections}")

        if COLLECTION_NAME not in collections:
            print(f"❌ Collection `{COLLECTION_NAME}` not found.")
            return

        collection = client.collections.get(COLLECTION_NAME)
        print(f"🔁 Wiping all objects in `{COLLECTION_NAME}`...")

        # Use the v4-compatible way to delete all objects
        result = collection.data.delete_many(where={})

        print(f"✅ Deleted {result['matches']} objects from `{COLLECTION_NAME}`.")

    except Exception as err:
        print(f"❌ Error while connecting or deleting: {err}")

    finally:
        client.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    wipe_all_objects()
