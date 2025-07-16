import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth

load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
)

def query_weaviate(query, top_k=3):
    response = client.collections.get("PageChunk").query.get(
        properties=["content", "url"]
    ).with_near_text({"concepts": [query]}).with_limit(top_k).do()

    return response.get("data", {}).get("Get", {}).get("PageChunk", [])

if __name__ == "__main__":
    print("Type your query (or 'exit' to quit):")
    while True:
        user_query = input("Query: ")
        if user_query.lower() == "exit":
            break
        results = query_weaviate(user_query)
        if not results:
            print("No results found.")
        else:
            for i, chunk in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"URL: {chunk['url']}")
                print(f"Content: {chunk['content'][:300]}{'...' if len(chunk['content']) > 300 else ''}")
    client.close()
