import weaviate
import uuid

def main():
    # 1. Connect to Weaviate
    client = weaviate.Client("http://localhost:8080")
    assert client.is_ready(), "Weaviate is not running!"

    # 2. Make sure 'PageChunk' exists
    assert "PageChunk" in [c['class'] for c in client.schema.get()["classes"]], "PageChunk schema missing!"

    # 3. Create and insert a test object (if needed)
    test_content = "Vector search is powerful and semantic!"
    test_uuid = str(uuid.uuid4())
    properties = {
        "chunk_id": f"test_{test_uuid}",
        "url": "https://example.org/test_chunk",
        "content": test_content,
        "hash": "testhash",
        "last_updated": "2025-07-18T12:00:00Z"
    }
    client.data_object.create(properties, class_name="PageChunk", uuid=test_uuid)
    print("Inserted test object with UUID:", test_uuid)

    # 4. Semantic query (nearText) for semantic match
    result = client.query.get("PageChunk", ["chunk_id", "url", "content"]).with_near_text({
        "concepts": ["semantic vector search"]
    }).with_limit(3).with_additional(['certainty', 'distance']).do()
    print("Top search result:\n", result["data"]["Get"]["PageChunk"][0])

    # 5. Clean up: Delete test object
    client.data_object.delete(uuid=test_uuid, class_name="PageChunk")

if __name__ == "__main__":
    main()
