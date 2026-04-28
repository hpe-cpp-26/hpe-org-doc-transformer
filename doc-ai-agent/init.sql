--without this postgres wont know how to handle vector types
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    path TEXT,
    group_id TEXT,
    content TEXT,
    embedding VECTOR(768),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS groups (
    id TEXT PRIMARY KEY,
    name TEXT,
    centroid VECTOR(768),
    doc_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    doc_id TEXT,
    group_id TEXT,
    chunk_text TEXT,
    embedding VECTOR(768)
);


--HNSW indexes for fast similarity search on vector columns
CREATE INDEX IF NOT EXISTS groups_centroid_hnsw_idx
    ON groups
    USING hnsw (centroid vector_cosine_ops);

CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops);