enterprise-rag-assistant/<br>
│<br>
├── app/<br>
│   ├── api/                    # FastAPI request/response layer<br>
│   │   ├── routes/             # Chat & streaming endpoints (SSE)<br>
│   │   ├── schemas.py          # Pydantic request/response models<br>
│   │   └── __init__.py<br>
│   │<br>
│   ├── core/                   # Core infrastructure utilities<br>
│   │   ├── config.py           # App-level configuration loading<br>
│   │   ├── logging.py          # Structured logging<br>
│   │   ├── security.py         # Security helpers (future-ready)<br>
│   │   ├── utils.py<br>
│   │   └── __init__.py<br>
│   │<br>
│   ├── rag/                    # RAG engine (heart of the system)<br>
│   │   ├── embeddings/         # Embedding providers<br>
│   │   │   ├── embedder_base.py<br>
│   │   │   ├── ollama_embedder.py<br>
│   │   │   ├── openai_embedder.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── ingest/             # Document ingestion pipeline<br>
│   │   │   ├── loader_pdf.py<br>
│   │   │   ├── loader_docx.py<br>
│   │   │   ├── chunker.py<br>
│   │   │   ├── pipeline.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── llm/                # LLM abstraction layer<br>
│   │   │   ├── llm_base.py<br>
│   │   │   ├── ollama_llm.py<br>
│   │   │   ├── openai_llm.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── policy/             # Governance & rewrite rules<br>
│   │   │   ├── rewrite_rules.py<br>
│   │   │   ├── registry.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── prompts/            # Prompt templates<br>
│   │   │   ├── system.txt<br>
│   │   │   ├── answer.txt<br>
│   │   │   ├── rewrite.txt<br>
│   │   │   └── loader.py<br>
│   │   │<br>
│   │   ├── retrieve/           # Retrieval & orchestration logic<br>
│   │   │   ├── retriever.py<br>
│   │   │   ├── query_router.py<br>
│   │   │   ├── query_rewriter.py<br>
│   │   │   ├── intent_router.py<br>
│   │   │   ├── prompt_builder.py<br>
│   │   │   ├── context_packer.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── store/              # Vector store abstraction<br>
│   │   │   ├── container.py<br>
│   │   │   ├── providers_factory.py<br>
│   │   │   └── __init__.py<br>
│   │   │<br>
│   │   ├── rag_factory.py      # Dependency wiring<br>
│   │   ├── rag_service.py      # End-to-end RAG orchestration<br>
│   │   └── __init__.py<br>
│   │<br>
│   ├── web/                    # FastAPI app entrypoint<br>
│   │   ├── main.py<br>
│   │   └── __init__.py<br>
│<br>
├── configs/                    # YAML-based configuration<br>
│   ├── app.yaml<br>
│   ├── rag.yaml<br>
│   ├── providers.yaml<br>
│   ├── policy.yaml<br>
│   └── ollama.yaml<br>
│<br>
├── data/<br>
│   ├── docs/                   # Source documents (AOA, MOA, rules, memos)<br>
│   └── samples/<br>
│<br>
├── scripts/                    # CLI & operational scripts<br>
│   ├── ingest_docs.py<br>
│   ├── ingest_minimal.py<br>
│   ├── retrieve_minimal.py<br>
│   ├── export_index.py<br>
│   └── smoke_test.py<br>
│<br>
├── storage/<br>
│   ├── vectordb/               # Vector database (Chroma / local)<br>
│   └── logs/<br>
│<br>
├── ui/                         # Lightweight frontend<br>
│   ├── index.html<br>
│   ├── script.js<br>
│   └── styles.css<br>
│<br>
├── docker-compose.yml<br>
├── Dockerfile<br>
├── requirements.txt<br>
├── .env.example<br>
└── README.md<br>
