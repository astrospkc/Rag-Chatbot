import time
import uuid
import json
import os
from typing import List, Dict, Any, Optional

import redisvl.exceptions as rvl_exc
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag

from dotenv import load_dotenv

from internal.core.config import settings
from internal.services.semantic_caching_service.redis_schema import schema,create_cache_schema, DOC_PREFIX

load_dotenv()

# Patch redisvl's missing index error detection to recognize Valkey's error phrasing:
# Valkey returns: "Index with name '...' not found in database 0"
if "not found" not in rvl_exc._MISSING_INDEX_ERROR_FRAGMENTS:
    rvl_exc._MISSING_INDEX_ERROR_FRAGMENTS = rvl_exc._MISSING_INDEX_ERROR_FRAGMENTS + (
        "not found in database",
        "not found",
    )


class SemanticCacheService:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        distance_threshold: float = 0.10,
        preferred_algorithm: str = "auto"  # "auto", "hnsw", or "flat"
    ):
        self.redis_url = redis_url or os.getenv("REDIS_URL") or getattr(settings, "REDIS_URL", "redis://localhost:6379")
        self.distance_threshold = distance_threshold
        self.preferred_algorithm = preferred_algorithm
        self.active_algorithm = "flat"
        
        # Start with the default schema
        self.schema = create_cache_schema("flat")
        self.index = SearchIndex(self.schema, redis_url=self.redis_url)
        self._init_dynamic_index()

    def _init_dynamic_index(self):
        """
        Dynamically initializes the index:
        1. If the index already exists, inspects and adopts the existing index.
        2. If 'auto' or 'hnsw', tries creating HNSW first.
        3. If the server (e.g. Valkey) rejects HNSW, dynamically falls back to FLAT.
        """
        try:
            if self.index.exists():
                print(f"[SemanticCache] Existing index '{self.index.name}' is ready.")
                return
        except Exception:
            pass  # Index not found, proceed to dynamic creation

        # Target algorithms to try in order
        algorithms_to_try = ["hnsw", "flat"] if self.preferred_algorithm == "auto" else [self.preferred_algorithm]

        for algo in algorithms_to_try:
            try:
                print(f"[SemanticCache] Attempting to create index with '{algo.upper()}' algorithm...")
                self.schema = create_cache_schema(algo)
                self.index = SearchIndex(self.schema, redis_url=self.redis_url)
                self.index.create(overwrite=False)
                self.active_algorithm = algo
                print(f"[SemanticCache] Successfully created '{self.index.name}' with '{algo.upper()}'!")
                return
            except Exception as e:
                print(f"[SemanticCache] '{algo.upper()}' creation failed ({e}).")
                if algo != algorithms_to_try[-1]:
                    print("[SemanticCache] Dynamically falling back to next algorithm...")

        print("[SemanticCache] Warning: Could not initialize index dynamically.")

    def check(
        self,
        query_vector: List[float],
        user_type: Optional[str] = None,
        distance_threshold: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Look for semantically similar cached queries.
        If user_type is guest or employee, anyone can access this data (no isolation filter).
        user_id and session_id are only for history, not for data filtering.
        """
        threshold = distance_threshold or self.distance_threshold

        # Anyone (guest or employee) can access cached data: no filter_expression
        vector_query = VectorQuery(
            vector=query_vector,
            vector_field_name="prompt_vector",
            num_results=1,
            return_fields=["prompt", "response", "sources", "user_type", "session_id"],
            filter_expression=None
        )
        # Valkey Search automatically sorts KNN results by vector distance ascending.
        # Calling sort_by([]) removes redisvl's redundant 'SORTBY vector_distance ASC'
        # which triggers "Index field 'vector_distance' does not exist" in Valkey.
        vector_query.sort_by([])

        try:
            results = self.index.query(vector_query)
            if results:
                best_match = results[0]
                distance = float(best_match.get("vector_distance", 1.0))
                similarity = 1.0 - distance

                # Step 3: Check if distance is within threshold (distance <= 0.10 means similarity >= 90%)
                if distance <= threshold:
                    print(f"[CACHE HIT] Distance {distance:.4f} <= {threshold} (Similarity: {similarity * 100:.1f}%) | Cached query: '{best_match.get('prompt')}'")
                    sources_raw = best_match.get("sources", "[]")
                    return {
                        "prompt": best_match.get("prompt"),
                        "answer": best_match.get("response"),
                        "sources": json.loads(sources_raw) if isinstance(sources_raw, str) else sources_raw,
                        "distance": distance,
                        "similarity": similarity,
                        "cached": True
                    }
                else:
                    print(f"[CACHE MISS] Best match too distant (Distance: {distance:.4f} > {threshold}, Similarity: {similarity * 100:.1f}%)")
        except Exception as e:
            print(f"[SemanticCache Check Error]: {e}")

        return None

    def store(
        self,
        prompt: str,
        response: str,
        sources: List[Dict[str, Any]],
        query_vector: List[float],
        user_type: str = "guest",
        user_id: str = "guest",
        session_id: Optional[str] = None,
        ttl: int = 86400  # Default 24 hours
    ):
        """
        Step 5: Store the new query + answer + embedding in Valkey.
        """
        doc_key = f"{DOC_PREFIX}:{uuid.uuid4().hex}"
        record = {
            "user_type": user_type,
            "user_id": user_id,
            "session_id": session_id or "",
            "prompt": prompt,
            "response": response,
            "sources": json.dumps(sources),
            "prompt_vector": query_vector,
            "created_at": time.time()
        }

        try:
            self.index.load([record], keys=[doc_key], ttl=ttl)
            print(f"[CACHE STORED] Successfully cached query for user_type='{user_type}'")
        except Exception as e:
            print(f"[SemanticCache Store Error]: {e}")