# 📚 Multi-Document Conversational RAG System

A production-ready **Multi-Document Conversational Retrieval-Augmented Generation (RAG)** application built using **FastAPI**, **LangChain**, **FAISS**, and **Google Gemini / Groq LLMs**.

The application allows users to upload multiple documents (PDF, DOCX, TXT), automatically indexes them using vector embeddings, and enables context-aware conversational question answering over the uploaded knowledge base.

---

## 🚀 Features

- 📄 Upload multiple documents simultaneously
- 💬 Chat with your documents using natural language
- 🧠 Retrieval-Augmented Generation (RAG)
- 🔍 Semantic Search using FAISS
- 📚 Conversation Memory
- ⚡ FastAPI REST API
- 🎯 Google Gemini / Groq LLM support
- 🔐 Environment-based API key management
- 🧩 Modular project architecture
- ✅ Unit & Integration Testing with Pytest
- 📊 Structured logging
- 📁 Session-based document storage

---

# Project Architecture

--
                User
                  │
                  ▼
         FastAPI REST API
                  │
      ┌───────────┴───────────┐
      │                       │
 Upload Documents        Ask Question
      │                       │
      ▼                       ▼
 Document Ingestion     Conversational RAG
      │                       │
 Text Splitting         Retrieve Relevant Chunks
      │                       │
 Embedding Generation        │
      │                       ▼
      ▼                  Google Gemini / Groq
   FAISS Vector Store         │
      │                       ▼
      └──────────► Final Response
``

---

# Tech Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| LLM Framework | LangChain |
| Embeddings | Google Gemini Embeddings |
| Vector Database | FAISS |
| LLM | Google Gemini / Groq |
| Language | Python 3.12+ |
| Testing | Pytest |
| Logging | Structlog |
| Environment | python-dotenv |

---

# Project Structure

``
LLMOPS/
│
├── multi_doc_chat/
│   ├── src/
│   │   ├── document_chat/
│   │   ├── document_ingestion/
│   │   ├── exception/
│   │   └── utils/
│   │
│   ├── logger/
│   └── config/
│
├── notebook/
├── static/
├── templates/
├── test/
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── uv.lock
```



# Installation

Clone the repository

```bash
git clone https://github.com/<your_username>/LLMOPS-Multi-Document-Rag.git

cd LLMOPS-Multi-Document-Rag
```

---

Create a virtual environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

---

Install dependencies

Using uv

```bash
uv sync
```

or

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

LLM_PROVIDER=google
```

---

# Running the Application

```bash
uvicorn main:app --reload
```

Application will be available at

```
http://127.0.0.1:8000
```

---

# API Endpoints

## Upload Documents

```
POST /upload
```

Uploads one or multiple documents.

Supported formats

- PDF
- DOCX
- TXT

---

## Chat

```
POST /chat
```

Ask questions based on uploaded documents.

Example

```json
{
    "session_id":"session_xxxxx",
    "query":"Summarize the uploaded document."
}
```

---

# Running Tests

```bash
uv run pytest
```

or

```bash
pytest
```

---

# Supported LLM Providers

| Provider | Supported |
|----------|-----------|
| Google Gemini | ✅ |
| Groq | ✅ |
| OpenAI | Easily Extendable |

---

# Supported File Types

- PDF
- DOCX
- TXT

---

# Logging

Application logs are generated using **Structlog**.

Example log

```json
{
    "timestamp":"2026-07-01T12:30:01Z",
    "event":"Document uploaded",
    "session":"session_xxxxxx"
}
```

---

# Testing

The project includes

- Unit Tests
- Integration Tests

Coverage includes

- Document ingestion
- FAISS indexing
- Conversational retrieval
- API endpoints

---

# Future Improvements

- Docker support
- Kubernetes deployment
- AWS deployment
- Authentication
- Persistent database
- Streaming responses
- Multi-user support
- Hybrid Search (BM25 + Vector Search)
- LangSmith tracing
- Redis caching

---

# Security

- API keys stored using `.env`
- No hardcoded credentials
- Session-based document isolation

---

# Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# License

This project is licensed under the MIT License.

---

# Author

**Sambeet Sabat**

GitHub:
https://github.com/sam17122004

LinkedIn:
www.linkedin.com/in/sambeet-sabat-640996304

---

⭐ If you found this project helpful, consider giving it a star.
