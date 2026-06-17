# HPE RAG Frontend

Frontend application for the HPE Retrieval-Augmented Generation (RAG) Search Service.

## Features

* Search interface for querying documents
* Integration with FastAPI Search Service
* Displays ranked search results
* Document viewer for viewing retrieved content
* Semantic search powered by pgvector and Ollama embeddings
* Cross-encoder reranked search results

## Prerequisites

Before running the frontend, ensure the following services are available:

* Node.js
* Docker Desktop
* PostgreSQL with pgvector
* Ollama
* FastAPI Search Service

Required Ollama model:

```bash
ollama pull nomic-embed-text
```

## Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Application runs at:

```text
http://localhost:5173
```

## Backend Requirements

The frontend expects the Search Service API to be running.

Start the backend:

```bash
python -m uvicorn app.main:app --port 8001
```

Swagger UI:

```text
http://127.0.0.1:8001/docs
```

## Search Flow

```text
User Query
    ↓
React Frontend
    ↓
FastAPI Search Service
    ↓
Ollama Embedding Generation
    ↓
PostgreSQL + pgvector Similarity Search
    ↓
Cross Encoder Reranking
    ↓
Ranked Results Returned
    ↓
Document Viewer
```

## Components

### ChatArea.jsx

* Accepts user queries
* Sends search requests to the backend
* Displays retrieved results

### SearchResultCard.jsx

* Displays document metadata
* Shows similarity scores
* Opens documents in the viewer

### DocumentViewer.jsx

* Displays selected document content
* Supports viewing retrieved chunks

### Message.jsx

* Handles chat and system messages

### Sidebar.jsx

* Reserved for future group/document navigation
* Currently not connected to backend group data

## Verified Functionality

* Frontend successfully communicates with FastAPI backend
* Search requests return relevant documents
* Document viewer opens selected results
* End-to-end search flow tested successfully
* Integration verified with seeded PostgreSQL data
