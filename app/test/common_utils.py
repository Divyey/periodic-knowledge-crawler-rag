import hashlib
import time

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def hash_chunk(chunk):
    return hashlib.sha256(chunk.encode("utf-8")).hexdigest()

def print_stats(name, start, end, chunks):
    print(f"\n{name} Results:")
    print(f"Time taken: {end - start:.2f} seconds")
    print(f"Total chars: {sum(len(c) for c in chunks)}")
    print(f"Chunks: {len(chunks)}")
    print(f"First chunk hash: {hash_chunk(chunks[0]) if chunks else 'N/A'}")
