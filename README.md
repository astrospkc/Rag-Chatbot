# RAG Chatbot Platform

A custom **Retrieval-Augmented Generation (RAG) Chatbot Service** built as a modern monorepo. This platform enables companies or individual users to upload/provide their domain documents, automatically chunk & index knowledge into a vector database, and generate tailored AI chatbots for their end users.

---

## 🌟 Key Concept & Vision

- **Document Ingestion**: Companies/users upload custom documentation (PDFs, Markdown, TXT, docs, API references, etc.).
- **Knowledge Processing (RAG)**: The platform parses and indexes documents into vector embeddings to allow semantic search retrieval.
- **Custom Chatbot Generation**: Generates customized chatbot instances that reference the uploaded domain knowledge.
- **End-User Access**: Businesses can embed or deploy their custom RAG chatbot to serve their own customers and clients with accurate, domain-specific answers.

---

## 🏗️ Tech Stack & Architecture

This project is structured as a **Turborepo** monorepo:

### **Frontend (`apps/web`)**
- **Framework**: React + Vite + TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router (`react-router-dom`)

### **Backend (`apps/api`)**
- **Framework**: Python FastAPI
- **Server**: Uvicorn
- **Package & Env Manager**: [`uv`](https://github.com/astral-sh/uv)

---

## 📁 Repository Structure

```text
rag_chatbot/
├── apps/
│   ├── api/            # Python FastAPI Backend (Managed with uv)
│   │   ├── main.py
│   │   ├── pyproject.toml / requirements.txt
│   │   └── package.json
│   └── web/            # React + Vite Frontend (Managed with pnpm)
│       ├── src/
│       └── package.json
├── packages/           # Shared monorepo packages/configs
├── package.json        # Root workspace configuration
├── pnpm-workspace.yaml # Workspace definitions
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v18+)
- **pnpm** (`npm i -g pnpm`)
- **Python 3.10+**
- **uv** (`pip install uv` or via script)

---

### 1. Installation

Install frontend & monorepo dependencies from the root directory:

```bash
pnpm install
```

Set up and install Python dependencies in `apps/api`:

```bash
cd apps/api
uv venv
uv pip install -r requirements.txt
cd ../..
```

---

### 2. Development

Run both the frontend and backend concurrently via Turborepo:

```bash
pnpm dev
```

Or run individual services:

- **Frontend (`apps/web`)**:
  ```bash
  pnpm dev --filter=web
  # Runs on http://localhost:5173
  ```

- **Backend (`apps/api`)**:
  ```bash
  pnpm dev --filter=api
  # Runs on http://localhost:8000
  ```

---

## 📝 Workflow Summary

1. **Upload**: User provides custom knowledge files through the Web UI.
2. **Embed & Store**: Backend processes documents into vector embeddings.
3. **Query**: End-user asks a question to the custom chatbot.
4. **Retrieve & Respond**: RAG retrieves relevant document contexts and provides accurate answers with sources.
