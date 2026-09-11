# 🤖 RAG Chatbot Platform

A modular, enterprise-ready **Retrieval-Augmented Generation (RAG) Platform** built as a modern full-stack monorepo. This platform enables users and organizations to upload domain-specific documents (PDFs, text, docs), execute distributed background ingestion, store vector embeddings, and serve high-accuracy context-aware AI chatbot responses.

---

## ⭐ Resume Highlights & Key Engineering Accomplishments

* **Modular RAG System Architecture**: Designed a Python RAG engine supporting customizable document loaders, chunking strategies (Recursive, Semantic), and extensible embedding providers (`OpenAIEmbeddings` / `OpenRouter`).
* **Asynchronous Task Processing with Celery & RabbitMQ**: Implemented distributed task queueing using **Celery** and **CloudAMQP (RabbitMQ)** to handle heavy CPU/IO-bound document parsing and vector generation off the main HTTP request loop.
* **Resilient API Integration & Rate Limiting**: Engineered custom embedding providers with built-in rate-limiting, exponential backoff/retries, and custom header configurations (`default_headers` for OpenRouter).
* **AWS Cloud Storage Integration**: Configured secure document ingestion workflows utilizing **AWS S3** presigned URLs for client-side uploads and server-side processing.
* **Database & Vector Search**: Structured persistence with **PostgreSQL + pgvector** for storing high-dimensional vector embeddings and metadata alongside document chunks.
* **High-Performance Monorepo Architecture**: backend (`FastAPI`, `uv`, `Python 3.14`, `golang` , `websockets`) within a **Turborepo + pnpm workspace**.

---

## 🛠️ Implemented Features

### 1. Document Processing & Ingestion Pipeline
- **Document Loading Engine**: Native loaders for handling multi-page PDF documents and raw text inputs.
- **Flexible Chunking Strategies**: 
  - `RecursiveChunker` with customizable chunk size and overlap.
  - Abstract `BaseChunker` interface for easy addition of Semantic or Hierarchical chunkers.
- **Asynchronous Ingestion Queues**: Heavy document ingestion tasks offloaded to **Celery worker queues** (`Queue("rag")`) using **RabbitMQ (CloudAMQP)** as the message broker.

### 2. Multi-Provider Embedding Engine
- **Framework-Agnostic Embedding Interface**: Abstract `BaseEmbeddingModel` & `EmbeddingFactory` pattern to easily swap embedding models.
- **OpenRouter & OpenAI Integration**: Seamless support for custom endpoints with required `HTTP-Referer` and `X-Title` header passing via `default_headers`.
- **Rate Limit & Resiliency Wrappers**: Custom `embed_documents_with_rate_limit` handling batching and request limits smoothly.

### 3. AWS S3 Integration
- **Presigned URL Generation**: Secure file upload flow via `boto3` for uploading documents to AWS S3 prior to background task processing.

### 4. Vector Persistence & Retrieval
- **pgvector Store Integration**: Persistence of embeddings and document chunk metadata into PostgreSQL using `pgvector`.

### 5. API Framework
- **FastAPI Endpoints**: RESTful API endpoints (`/documents`, `/doc`) with background task handoff.


---

## 🚀 Upcoming Features (Roadmap)

- [ ] **Hybrid Search & Re-ranking**: Combine BM25 keyword search with dense vector similarity search, topped with Cohere/BGE cross-encoder re-ranking.
- [ ] **Multi-Tenant User Management & Auth**: JWT-based authentication with role-based access control (RBAC) to allow multiple isolated workspaces.
- [ ] **Interactive Citation & Source Attribution**: UI preview highlighting exact page numbers and PDF text snippets used to generate responses.
- [ ] **FAISS On-Demand Vector Indexing**: Local/ephemeral FAISS index creation for ultra-fast in-memory document retrieval.
- [ ] **Streaming Chat Responses**: Real-time server-sent events (SSE) or WebSockets for token-by-token streaming LLM responses.
- [ ] **Observability & Analytics**: Integration with LangSmith for tracking RAG retrieval accuracy, latency, and token costs.

---

## 🏗️ Architecture & Tech Stack

```text
rag_chatbot/
├── apps/
│   ├── api/                # Python FastAPI Backend
│   │   ├── internal/
│   │   │   ├── handlers/   # API Endpoint Controllers (/doc, /documents)
│   │   │   ├── rag/        # Loaders, Chunkers, Embedding Providers & Adapters
│   │   │   ├── services/   # Celery, RabbitMQ & AWS S3 integration
│   │   │   └── tasks/      # Background Celery Ingestion Tasks
│   │   ├── main.py
│   │   └── pyproject.toml
│   └── web/                # React + Vite + TypeScript Frontend
├── packages/               # Shared Monorepo Configurations
├── pnpm-workspace.yaml     # Monorepo Workspace Config
├── turbo.json              # Turborepo Task Pipeline Config
└── README.md
```

### Stack Overview
* **Backend**: FastAPI, Python 3.10+, `uv` package manager
* **Task Queue & Messaging**: Celery, RabbitMQ (CloudAMQP)
* **Cloud & Storage**: AWS S3 (`boto3`), PostgreSQL (`pgvector`)
* **AI Engine & Tools**: LangChain, OpenRouter API, OpenAI Embeddings

---

## 💻 Getting Started

### Prerequisites
- **Node.js** (v18+) & **pnpm**
- **Python** (v3.10+) & **uv**
- **RabbitMQ / CloudAMQP Instance** & **PostgreSQL + pgvector**

### 1. Installation

Install frontend & monorepo dependencies:
```bash
pnpm install
```

Set up Python environment in `apps/api`:
```bash
cd apps/api
uv venv
cd ../..
```

### 2. Running Locally

Run both frontend & backend concurrently:
```bash
pnpm dev
```

Run Celery background worker:
```bash
cd apps/api
celery -A internal.tasks.rag_tasks worker --loglevel=info -Q rag
```
