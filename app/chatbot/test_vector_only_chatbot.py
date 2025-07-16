from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

QUESTION = "What is the price of the blue silk kurta?"

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

response = collection.query.near_text(
    query=QUESTION,
    limit=1,
    return_properties=["url", "content", "last_updated"]
)

print("\n🧠 Answer from Vector DB:\n")

if not response.objects:
    print("❌ No response found in vector DB!")
else:
    for obj in response.objects:
        print(f"📄 URL: {obj.properties['url']}")
        print(f"📝 Content snippet:\n{obj.properties['content'][:500]}...")
        print(f"📅 Last Updated: {obj.properties['last_updated']}\n")

client.close()
