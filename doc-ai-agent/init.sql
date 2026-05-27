--without this postgres wont know how to handle vector types
CREATE EXTENSION IF NOT EXISTS vector;



CREATE TABLE IF NOT EXISTS groups (
    id TEXT PRIMARY KEY,
    group_name TEXT not NULL,
    group_summary TEXT,
    doc_count INT DEFAULT 0,
    proto_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    doc_path TEXT,
    group_id TEXT REFERENCES groups(id),
    content TEXT,
    segment_count INT default 1,
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_segments (
    id SERIAL PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    group_id TEXT REFERENCES groups(id),
    segment_index INT NOT NULL default 0,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()

    unique(doc_id, segment_index)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    doc_id TEXT not NULL REFERENCES documents(id) on DELETE CASCADE,
    group_id TEXT REFERENCES groups(id),
    chunk_index INT NOT NULL,
    total_chunks INT NOT NULL,
    chunk_text TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW(),

    unique(doc_id, chunk_index)
);


CREATE TABLE IF NOT EXISTS group_prototypes (
    id SERIAL PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES groups(id) on DELETE CASCADE,
    proto_index INT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (group_id, proto_index) 
);

CREATE TABLE IF NOT EXISTS prototype_buffer (
    id              SERIAL PRIMARY KEY,
    group_id        TEXT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    segment_index   INT NOT NULL DEFAULT 0,
    embedding       VECTOR(768) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS doc_embedding_cache (
    doc_id TEXT PRIMARY KEY,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()
);



--HNSW indexes for fast similarity search on vector columns
CREATE INDEX IF NOT EXISTS idx_proto_embedding_hnsw
    ON group_prototypes
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 32, ef_construction = 128);

--chunk search (fine-grained retrieval within a group)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops)
    

--doc segment search (used during prototype recompute)
CREATE INDEX IF NOT EXISTS idx_segments_embedding_hnsw
    ON document_segments
    USING hnsw (embedding vector_cosine_ops)
  

-- fast group filtering on chunks and segments
CREATE INDEX IF NOT EXISTS idx_chunks_group_id
    ON document_chunks (group_id);

CREATE INDEX IF NOT EXISTS idx_segments_group_id
    ON document_segments (group_id);

CREATE INDEX IF NOT EXISTS idx_buffer_group_id
    ON prototype_buffer (group_id);

CREATE INDEX IF NOT EXISTS idx_documents_group_id
    ON documents (group_id);


CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops);
