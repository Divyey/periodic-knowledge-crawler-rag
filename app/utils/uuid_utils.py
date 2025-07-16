import uuid

def get_uuid_from_chunk_id(chunk_id: str) -> str:
    """Generate deterministic UUID from chunk ID."""
    namespace = uuid.UUID("00000000-0000-0000-0000-000000000000")
    return str(uuid.uuid5(namespace, chunk_id))
