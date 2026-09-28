import os
from typing import Literal
from redisvl.schema import IndexSchema

INDEX_NAME = os.getenv("CACHE_INDEX_NAME", "rag-semantic-cache-idx")
DOC_PREFIX = "cache:query"

def create_cache_schema(algorithm: Literal["flat", "hnsw"] = "flat") -> IndexSchema:
    """Dynamically builds a schema configured with either FLAT or HNSW indexing."""
    return IndexSchema.from_dict({
        "index": {
            "name": INDEX_NAME,
            "prefix": DOC_PREFIX,
            "storage_type": "json"
        },
        "fields": [
            # 1. Access Control / Metadata
            {"name": "user_type", "type": "tag"},
            {"name": "user_id", "type": "tag"},
            {"name": "session_id", "type": "tag"},

            # 2. Cached Q&A
            {"name": "prompt", "type": "text"},
            {"name": "response", "type": "text"},
            {"name": "sources", "type": "text"},

            # 3. Vector Embedding (Dynamically FLAT or HNSW)
            {
                "name": "prompt_vector",
                "type": "vector",
                "attrs": {
                    "algorithm": algorithm,
                    "datatype": "float32",
                    "dims": 768,
                    "distance_metric": "cosine"
                }
            },

            # 4. Timestamp
            {"name": "created_at", "type": "numeric"}
        ]
    })

# Default schema
schema = create_cache_schema("flat")