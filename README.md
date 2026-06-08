## Search Service

The Search Service implements the retrieval layer of the RAG (Retrieval-Augmented Generation) pipeline. It accepts a user query, generates embeddings using Ollama (`nomic-embed-text`), performs semantic similarity search on document embeddings stored in PostgreSQL with pgvector, and returns the most relevant document chunks.

### Features
- Semantic search using vector embeddings
- Embedding generation through Ollama
- PostgreSQL integration with pgvector
- Cosine similarity-based retrieval
- FastAPI REST endpoint for querying documents
- Retrieval of top matching document chunks

### Retrieval Flow

User Query  
↓  
Generate Embedding (Ollama)  
↓  
Vector Similarity Search (pgvector)  
↓  
Retrieve Top Matching Chunks  
↓  
Return Ranked Results  

### Technologies Used
- FastAPI
- PostgreSQL
- pgvector
- Ollama
- nomic-embed-text
- Psycopg

### Running the Service

1. Start Ollama:

```bash
ollama serve
```

2. Ensure the embedding model is available:
ollama pull nomic-embed-text

3. Start the FastAPI application:
uvicorn app.main:app --reload

4. Open Swagger UI:
http://127.0.0.1:8000/docs

### Alt method

1. Start the FastAPI application:
uvicorn app.main:app --reload

2. Run the test
python test_search.py




