-- Enable pgvector extension (required for vector / halfvec types)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table to store documents with embeddings
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  embedding vector(768),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for vector search over document embeddings
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx 
ON documents USING hnsw (embedding vector_cosine_ops);


