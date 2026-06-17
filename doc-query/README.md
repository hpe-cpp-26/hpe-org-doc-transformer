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



