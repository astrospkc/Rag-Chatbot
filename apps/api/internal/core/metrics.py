from prometheus_client import Counter, Histogram

# Request counters (by user type)
REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total number of RAG requests processed",
    ["user_type"],
)

# Semantic cache metrics
CACHE_HITS = Counter(
    "semantic_cache_hits_total",
    "Number of cache hits",
    ["user_type"],
)
CACHE_MISSES = Counter(
    "semantic_cache_misses_total",
    "Number of cache misses",
    ["user_type"],
)
CACHE_LATENCY = Histogram(
    "semantic_cache_lookup_seconds",
    "Latency of semantic cache lookup (seconds)",
    ["user_type"],
)

# Vector search latency
VECTOR_SEARCH_LATENCY = Histogram(
    "vector_search_latency_seconds",
    "Latency of vector database search (seconds)",
)

# LLM inference latency
LLM_LATENCY = Histogram(
    "llm_inference_latency_seconds",
    "Latency of LLM call (seconds)",
)

