from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams
from weaviate.classes.config import Property, Configure, DataType

COLLECTION_NAME = "PageChunk"

def setup_schema():
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

    client.connect()
    print("✅ Connected to Weaviate")

    # Drop if exists
    if COLLECTION_NAME in client.collections.list_all():
        print(f"🗑 Dropping `{COLLECTION_NAME}`...")
        client.collections.delete(COLLECTION_NAME)

    # Create collection with OpenAI vectorization
    client.collections.create(
        name=COLLECTION_NAME,
        properties=[
            Property(name="chunk_id", data_type=DataType.TEXT),
            Property(name="url", data_type=DataType.TEXT),
            Property(name="content", data_type=DataType.TEXT),
            Property(name="hash", data_type=DataType.TEXT),
            Property(name="last_updated", data_type=DataType.TEXT),
        ],
        vector_config=Configure.Vectors.text2vec_openai()
    )

    print(f"✅ Created collection `{COLLECTION_NAME}` with OpenAI embedding.")
    client.close()
    print("🔒 Connection closed.")

if __name__ == "__main__":
    setup_schema()
