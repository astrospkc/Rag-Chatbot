
-- Table to store documents 
CREATE TABLE IF NOT EXISTS uploaded_documents (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT,
  status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
  processing_error TEXT,          -- Any error message
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for querying documents by status or creation date
CREATE INDEX IF NOT EXISTS idx_uploaded_documents_status ON uploaded_documents(status);



