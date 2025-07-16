import re
import hashlib

def compute_hash(text: str) -> str:
    """
    Normalize and compute SHA-256 hash of content.
    """
    cleaned = re.sub(r'[\s₹\u20b9,.]', '', text).lower()
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
