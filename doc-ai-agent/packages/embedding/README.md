# Embedding Package

Generates 768-dimensional embeddings for normalized documents using Ollama.

## Requirements

- Ollama running locally on port 11434
- Model: `nomic-embed-text` (768 dimensions)

Start Ollama:
```bash
ollama serve
ollama pull nomic-embed-text
```

## Usage

```python
from embedding import generate_embedding

embedding = generate_embedding("Your document text here")
# Returns: list[float] with 768 dimensions
```
