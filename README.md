## Search Service

The Search Service implements the retrieval and response generation layer of the RAG (Retrieval-Augmented Generation) pipeline. It accepts a user query, generates embeddings using Ollama (`nomic-embed-text`), performs semantic similarity search on document embeddings stored in PostgreSQL with pgvector, re-ranks the retrieved results using a Cross-Encoder model, and generates a structured response using Gemini.

### Features

- Semantic search using vector embeddings
- Embedding generation through Ollama (`nomic-embed-text`)
- PostgreSQL integration with pgvector
- Cosine similarity-based retrieval
- Cross-Encoder re-ranking for improved relevance
- Gemini-powered answer generation
- Structured responses with summaries and key points
- Source document tracking with document paths
- Prompt injection safeguards for secure RAG responses
- FastAPI REST API for document querying

### Retrieval Pipeline

User Query  
↓  
Generate Embedding (Ollama)  
↓  
Vector Similarity Search (pgvector)  
↓  
Retrieve Top Matching Chunks  
↓  
Cross-Encoder Re-ranking  
↓  
Generate Structured Answer (Gemini)  
↓  
Return Answer + Source Metadata

### API Response

The service returns:

- Structured answer generated from retrieved context
- Key points summary
- Source document metadata (`doc_id`, `doc_path`)
- Confidence score
- Relevant source references

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




