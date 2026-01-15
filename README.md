# Enterprise RAG Assistant

## Demo Video
[![Enterprise RAG Assistant Demo] (demo/demo-thumbnail.png)](demo/demo.mp4)

## Overview 
**Enterprise RAG Assistant** is a production-oriented Retrieval-Augmented Generation (RAG) system designed for **document-grounded question answering** with clear citations , deterministic behavior, and deployment readiness.
<br>
<br>
The system enables users to ask natural-language questions over a private document corpus (e.g. PDFs, policies, internal memos, MOA, AOA) and receive: <br>
- Context-aware answers grounded strictly in retrieved documents
- Explicit source citations (document + page)
- Controlled fallback behavior when information is insufficient
- A clean ChatGPT-like UI with streaming resposnes
- A Dockerized backend suitable for local, on-prem, or cloud deployment

This project focuses on **engineering correctness and reliability**, not just model output - emphasizing retrieval quality, prompt discipline, citation control, and operational clarity.

## Problem Statement

Large Language Models (LLMs) are not reliable when answering questions about **private or domain-specific documents**. Out of the box, they tend to:
- Hallucinate answers not present in the source material
- Blend prior knowledge with retrieved content
- Return confident but unverifiable responses
- Provide no clear indication of where information came from

For enterprise and internal-use cases (policies, legal documents, internal knowledge bases), this behavior is unacceptable.

A robust system must:
- Retrieve only the most relevant document context
- Ground answers strictly in retrieved evidence
- Detect when information is insufficient and refuse to speculate
- Provide transparent citations for every response
- Remain performant and predictable under deployment constraints

This project addresses these challenges by implementing a **controlled, citation-aware RAG pipeline** that prioritizes correctness, traceability, and operational reliability over raw generative freedom.

## Key Features

### 🔎 Retrieval-First Answering
- Vector-based document retrieval using **Chroma**
- Configurable `top_k` and `retrieval_pool_k` for precision vs recall control
- Query rewriting to improve retrieval quality across follow-up questions

### 🧠 Controlled Prompt Construction
- Explicit separation of:
  - System instructions
  - Conversation history
  - Retrieved context
  - User question
- No blind LLM calls — prompt is built **only after retrieval validation**

### 🚫 No-Answer / Deny Path
- Automatically detects when retrieved context is insufficient
- Returns a deterministic, safe response instead of hallucinating
- Ensures **zero citations** are shown when no answer is generated

### 📚 Citation-Aware Responses
- Citations generated directly from retrieved document metadata
- Deduplication and ranking of sources
- Limited to **top-N used sources** for clarity
- Transparent document, page, and section attribution

### 💬 Streaming Chat Interface
- Server-Sent Events (SSE) token streaming
- Stop / cancel generation mid-response
- Real-time UI updates without blocking

### 🧾 Session-Scoped Chat History
- In-memory multi-chat support per browser session
- Sidebar chat switching without persistence
- History isolation between conversations

### 🎨 Minimal, Production-Ready UI
- ChatGPT-style layout with sidebar
- Dark / light theme toggle
- Auto-resizing input, typing indicators, citation expanders

### ⚙️ Config-Driven Architecture
- YAML-based configuration for:
  - Models
  - Thresholds
  - Retrieval parameters
- Environment variable overrides for deployment flexibility

### 🐳 Dockerized Deployment
- Fully containerized backend
- Compatible with local, VM, or cloud deployment
- No code changes required between environments

## Architecture Overview

The system follows a **retrieval-first, validation-driven RAG pipeline** designed to prevent hallucinations and ensure traceable answers.

### High-Level Flow

User Query 
↓
Intent & Query Routing<br>
↓<br>
Query Rewrite (optional)<br>
↓<br>
Vector Retrieval (Chroma)<br>
↓

Retrieval Validation<br>
├── No / Weak Match → Deterministic No-Answer Response<br>
└── Valid Match<br>
↓<br>
Prompt Construction<br>
↓<br>
LLM Generation (Streaming or Non-Streaming)<br>
↓<br>
Citation Selection & Response Delivery <br>


### Core Design Principles

#### 1. Retrieval Before Generation
The LLM is **never called blindly**.  
If retrieval fails quality checks, the system exits early with a safe response.

#### 2. Explicit Prompt Assembly
Prompts are assembled from clearly separated components:
- System instructions
- Filtered conversation history
- Retrieved document context
- Current user question

This prevents instruction leakage and response drift.

#### 3. Distance-Based Validation
Retrieved documents are validated using embedding distance thresholds:
- **Good** → normal answer
- **Weak** → restricted answer mode
- **Invalid** → deny / no-answer path

#### 4. Citation-Grounded Answers
Only documents used in the final answer are surfaced as citations.
This ensures:
- No irrelevant sources
- No hallucinated references
- Clear traceability

#### 5. Streaming-Safe Execution
Streaming responses:
- Emit citations first
- Stream tokens incrementally
- Support mid-generation cancellation
- Preserve UI responsiveness

---

### Component Breakdown

| Component       | Responsibility                 |
|-----------------|--------------------------------|
| `Retriever`     | Vector search & ranking        |
| `QueryRouter`   | Dataset / namespace routing    |
| `PromptBuilder` | Structured prompt construction |
| `RAGService`    | Orchestration & validation     |
| `LLM Provider`  | Text generation                |
| `Chat API`      | REST + streaming endpoints     |
| `UI`            | Session-based chat interface   |

---

### Failure-Safe Behavior

- ❌ No documents → no LLM call
- ❌ Weak retrieval → controlled answer mode
- ❌ Deny / closing intent → deterministic response
- ❌ User cancellation → clean stop without state corruption

## ⚙️ Configuration & Customization

This project is fully **configuration-driven**, allowing behavior changes without modifying application code.  
All critical components are controlled via YAML files with optional environment overrides.

---

### Configuration Files

#### `app.yaml`
Controls application-level behavior.

- Application name
- Environment (`dev` / `prod`)
- Logging level
- CORS configuration

Used to adapt runtime behavior across environments.

---

#### `rag.yaml`
Defines Retrieval-Augmented Generation behavior.

Configurable parameters include:

- `collection_name` – vector database collection
- `top_k` – number of chunks used in final context
- `retrieval_pool_k` – initial retrieval candidate pool
- `max_context_chars` – context size bound
- `max_history` – number of past user turns
- Distance thresholds:
  - `good_threshold`
  - `weak_threshold`
- Rewrite and intent-routing controls

This enables safe tuning of recall vs precision without code changes.

---

#### `providers.yaml`
Controls model providers and backends.

- LLM provider selection
- Embedding provider selection
- Model names
- Timeouts
- Provider-specific parameters

Supports easy switching between:
- Local inference
- Containerized services
- Cloud-hosted providers

---

#### `ollama.yaml`
Ollama-specific configuration.

- API base URL
- Model names for LLM and embeddings
- Request timeouts

This file is overridden automatically via environment variables when deployed in Docker or cloud environments.

---

### Environment Variable Overrides

The system supports standard environment-based overrides for deployment:

- Local development
- Docker containers
- Cloud platforms

Environment variables always take precedence over YAML defaults, enabling:

- Zero-code deployment changes
- Secure secret handling
- Environment-specific routing

---

### Why This Matters

This configuration approach ensures the system is:

- ✅ Environment-agnostic  
- ✅ Easy to tune and experiment  
- ✅ Safe for production deployment  
- ✅ Aligned with enterprise RAG standards  

---

### Design Philosophy

> **Code defines behavior. Configuration defines policy.**

## 🚀 Deployment

This project is designed to be **production-ready**, **containerized**, and **cloud-agnostic**.

The same codebase runs across:
- Local development
- Docker containers
- Cloud container platforms (AWS / GCP / Azure)

No code changes are required between environments — only configuration values differ.

---

### 🐳 Docker Deployment (Recommended)

The project includes a Dockerfile and `docker-compose.yml` for easy setup and execution.

To build and start the application:

```bash
docker compose build
docker compose up
```

## System Architecture Overview

This system consists of the following core components:

- **FastAPI backend**
- **Chroma vector database** (persistent storage)
- **Connectivity to the Ollama inference server**

---

## ⚙️ Environment-Based Configuration

All environment-specific settings are injected using environment variables.

This enables a clean separation between:

- Development
- Staging
- Production

### Example Environment Variables

```env
APP_ENV=prod
OLLAMA_API_URL=http://ollama:11434
CHROMA_PERSIST_DIR=/data/chroma
```

## 📂 Project Structure

The repository follows a **modular, production-oriented layout** designed for clarity, scalability, and maintainability.

app/
  api/        # FastAPI endpoints
  rag/        # Retrieval, prompts, policies
  core/       # Config & logging
configs/      # YAML configuration
data/         # Source documents
ui/           # Frontend
storage/      # Vector DB & logs

## Deep Dive: Architecture (Optional)
➡️ See [Architecture Deep Dive](docs/architecture.md)

Key principles:
- Clear separation of concerns
- Provider-agnostic design
- Easy extension and replacement of components
- Minimal coupling between UI, API, and RAG logic

## 🧠 Design Decisions

This project follows **industry-standard RAG architecture patterns** rather than experimental or toy implementations.

### 1. Separation of Retrieval and Generation
Retrieval is completed **before** any LLM invocation.  
If retrieval fails or is weak, the model is **not called**, preventing hallucinations.

### 2. Retrieval Pooling + Top-K Selection
- A larger retrieval pool (`retrieval_pool_k`) is fetched from the vector store
- Results are deduplicated and ranked
- Only the top-K most relevant chunks are passed to the prompt

This improves recall without polluting the prompt context.

### 3. Prompt Construction Pipeline
Prompt building is treated as a **deterministic step**, separate from inference.

Steps:
1. User history filtering
2. Optional query rewriting
3. Context packing
4. Prompt rendering
5. Citation selection

This makes debugging and auditing straightforward.

### 4. Streaming-First LLM Interface
The system supports both:
- Standard completion
- Token-by-token streaming (SSE)

Streaming is implemented without changing retrieval or prompt logic.

### 5. Provider-Agnostic Architecture
- LLMs
- Embedders
- Vector stores

All are abstracted behind interfaces, allowing future replacement (OpenAI, cloud LLMs, FAISS, etc.) without architectural changes.


## 🔐 Security & Privacy

This project is designed for **enterprise and internal deployments**, where data privacy is critical.

### Local-First Inference
- LLM inference runs via Ollama
- No data is sent to external APIs by default
- Suitable for air-gapped or restricted environments

### Controlled Knowledge Access
- The model is explicitly instructed to use **only retrieved context**
- If information is missing, the system returns a denial response
- This prevents knowledge leakage and hallucinated answers

### Configuration via Environment Variables
- No secrets are hardcoded
- All sensitive values are injected via environment variables
- YAML files provide defaults but are overrideable in production

### Stateless API Design
- No user sessions stored server-side
- No conversation persistence beyond request scope
- Compatible with secure internal gateways and API proxies

This design aligns with enterprise security reviews and compliance expectations.

## ✨ Features

### 🔎 Retrieval-Augmented Generation (RAG)
- Semantic document retrieval using vector search
- Chunked ingestion with configurable overlap and size
- Distance-based relevance filtering to prevent low-confidence answers
- Context packing optimized for long legal and policy documents

---

### 🧠 Intent-Aware Query Handling
- Built-in intent routing for:
  - Conversational closings (e.g., “thanks”, “that’s all”)
  - No-answer scenarios when content is unavailable
- Prevents unnecessary LLM calls for non-informational queries
- Ensures predictable, controlled assistant behavior

---

### 📚 Citation-Grounded Responses
- Answers are generated **only from retrieved documents**
- Citations are:
  - Filtered to include **only sources actually used**
  - Limited to top-K most relevant references
  - Displayed separately from the response for clarity
- Zero citations are returned for deny / no-answer paths

---

### ⚡ Streaming Responses (SSE)
- Token-level streaming via Server-Sent Events (SSE)
- Immediate partial responses for improved UX
- Clean separation of:
  - Citations event
  - Token stream
  - Completion signal

---

### 🔄 Config-Driven Architecture
- Behavior controlled via YAML configuration (no code changes required):
  - Retrieval thresholds
  - Top-K selection
  - Provider switching
  - Policy rules
- Environment-specific overrides supported (local vs production)

---

### 🤖 Pluggable LLM & Embeddings
- Supports multiple providers:
  - Local LLMs via **Ollama**
  - Cloud LLMs via **OpenAI**
- Embedding providers are fully swappable
- Designed for vendor neutrality and cost control

---

### 🛡️ Safety & Hallucination Control
- Hard blocking of answers when retrieval confidence is low
- Explicit no-answer messaging instead of speculative responses
- Policy-driven rewrite and validation rules
- Logging of retrieval distances for auditability

---

### 🧩 Modular, Production-Ready Design
- Clear separation of concerns:
  - Ingestion
  - Retrieval
  - Prompt construction
  - Policy enforcement
  - Streaming API
- Easy to extend with new:
  - Document loaders
  - Policies
  - Providers
- Suitable for enterprise internal knowledge bases

---

### 🧩 Modular, Production-Ready Design
- Clear separation of concerns:
  - Ingestion
  - Retrieval
  - Prompt construction
  - Policy enforcement
  - Streaming API
- Easy to extend with new:
  - Document loaders
  - Policies
  - Providers
- Suitable for enterprise internal knowledge bases

## 🧪 Example Queries

Below are representative examples demonstrating how the system behaves across common and edge-case scenarios.

---

### ✅ Answerable, Document-Grounded Queries

**User Query** : What is the quorum requirement for board meetings?

**System Behavior**
- Retrieves relevant sections from governing documents
- Generates a grounded response using only retrieved context
- Returns citations referencing document name and page numbers

---

**User Query** : When is an audit committee required?

**System Behavior**
- Identifies relevant regulatory clauses
- Summarizes requirements concisely
- Includes only the sources actually used in the answer

---

### ⚠️ Weak Match / Low Confidence Queries

**User Query** : Explain compliance responsibilities for overseas subsidiaries.


**System Behavior**
- Detects weak retrieval confidence
- Enforces stricter response rules
- Answers only if a direct supporting quote exists
- Otherwise, returns a no-answer response without citations

---

### 🚫 No-Answer / Out-of-Scope Queries

**User Query** : What are the tax implications of cryptocurrency trading?

**System Behavior**
- No relevant documents retrieved
- Returns a clear deny message
- No LLM speculation
- No citations included

---

### 💬 Conversational Closings

**User Query** : Thanks, that answers my question.

**System Behavior**
- Intent-aware routing detects conversational closing
- Responds politely without invoking retrieval or LLM generation
- No citations returned

---

### 🔁 Follow-Up Queries (Context-Aware)

**User Query** : Does that rule apply to private companies as well?

**System Behavior**
- Uses recent user-only conversation history
- Rewrites the query for clarity
- Retrieves relevant follow-up context
- Avoids repetition of prior answers

---

These examples illustrate how the system balances **precision**, **safety**, and **usability** while maintaining strict control over hallucinations and source attribution.


## ⚙️ Configuration Reference

This project is fully **configuration-driven**, allowing easy tuning for local development, Docker, and cloud deployment without changing application logic.

All core behavior (retrieval depth, thresholds, models, endpoints) is controlled via **YAML + environment overrides**, following industry best practices.

---

### 1. Configuration Files

#### `configs/app.yaml`

Controls application-level behavior.

**Key parameters:**
- History limits
- Retrieval thresholds
- Citation limits
- Weak-answer behavior

**Example:**
```yaml
rag:
  max_history: 6
  rewrite_max_history_turns: 4
  top_k: 5
  retrieval_pool_k: 25
  good_threshold: 0.35
  weak_threshold: 0.55
  require_quotes_in_weak_mode: true
```
#### `configs/ollama.yaml`

Defines the LLM and embedding model configuration.

**Example:**
```yaml
ollama:
  model: mistral
  embedding_model: nomic-embed-text
  timeout: 120
```

⚠️ Values in this file are defaults and may be overridden by environment variables.

---

### 2. Environment Variables

Environment variables always override YAML values, enabling seamless switching between:

- Local development
- Docker containers
- Cloud deployment

| Variable               | Purpose                   |
|------------------------|---------------------------|
| OLLAMA_API_URL         | Ollama server endpoint    |
| OLLAMA_MODEL           | LLM model name            |
| OLLAMA_EMBED_MODEL     | Embedding model           |
| CHROMA_PERSIST_DIR     | Vector store location     |
| LOG_LEVEL              | Application log level     |

**Example:**
```bash
export OLLAMA_API_URL=http://localhost:11434
export OLLAMA_MODEL=mistral
export OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

### 3. Local vs Docker vs Cloud

| Environment | Configuration Source                     |
|-------------|------------------------------------------|
| Local       | YAML + `.env`                            |
| Docker      | `docker-compose.yml` environment section |
| Cloud       | Platform-provided environment variables  |

No code changes are required when switching environments.

---

### 4. Threshold Tuning (RAG Guardrails)

| Parameter            | Description                      |
|----------------------|----------------------------------|
| top_k                | Final number of documents used   |
| retrieval_pool_k     | Initial retrieval pool           |
| good_threshold       | High confidence cutoff           |
| weak_threshold       | Deny / no-answer cutoff          |

This enables:

- Strict hallucination prevention
- Graceful deny responses
- Controlled citation exposure

---

### 5. Safe Defaults

The default configuration is designed to:

- Prefer **no answer over hallucination**
- Limit citations to **used context only**
- Prevent irrelevant document leakage

These defaults can be safely adjusted for different domains.

##  🚀 Deployment (Local & Docker)

The system is designed to run consistently across **local development**, **Docker**, and **cloud environments**.

### Supported Modes
- **Local (Python / venv / Conda)**  
  Useful for debugging, development, and experimentation.
- **Docker (Production-like)**  
  Ensures reproducibility and environment parity.
- **Cloud-ready**  
  Can be deployed on any container platform (AWS ECS, Azure Container Apps, GCP Cloud Run, etc.).

### Configuration Strategy
- **YAML files** define default behavior
- **Environment variables** override YAML for environment-specific values  
  (e.g., API URLs, model endpoints)

This pattern avoids hard-coding URLs and enables seamless switching between local, Docker, and cloud setups.

---

## 🎏 Streaming & UI Design

The frontend uses **Server-Sent Events (SSE)** to stream tokens in real time, providing a ChatGPT-like experience.

### UI Highlights
- Streaming token responses
- Typing indicator
- Stop / interrupt generation
- Session-based chat history (non-persistent)
- Inline source citations
- Graceful handling of deny / no-answer responses

The UI is intentionally **minimal, neutral, and enterprise-styled**, focusing on clarity and trust rather than animations or effects.

---

## 🔮 Limitations & Future Improvements

### Current Limitations
- No authentication or persistent user accounts
- Chat history resets on refresh
- No GPU acceleration by default
- Basic citation matching (string-based)

### Possible Future Improvements
- Token-level streaming citations
- Smarter citation-to-answer alignment
- Persistent chat sessions (optional auth)
- Async batching & caching
- GPU-backed inference (optional)
- Advanced observability (metrics, tracing)

These are intentionally deferred to keep the current system **stable, explainable, and base for implementation production-safe **.
