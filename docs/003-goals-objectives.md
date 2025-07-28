# 003 Goals and Objectives

This project aims to prototype a robust retrieval-augmented generation (RAG) system with the following goals:

- **Automated Periodic Crawling:** Build a scalable crawler that respects robots.txt, parses sitemaps, and scrapes product pages regularly.
- **Efficient Content Processing:** Chunk large page content intelligently and hash chunks to detect changes for minimal reindexing.
- **Seamless Upsert Pipeline:** Integrate Weaviate vector database client for incremental inserts and updates.
- **Interactive Voice/Text Chatbot:** Develop a Streamlit-based chatbot supporting voice input (Whisper) and text, enhanced by OpenAI GPT-3.5's generative capabilities.
- **Complete Pipeline Orchestration:** Use APScheduler to schedule and automate crawling and indexing every 30 minutes.
- **Modular & Maintainable Codebase:** Ensure clean separation of concerns and extensibility.

Deliverables:

- Working crawler code supporting concurrent multi-threaded scraping.
- Upsert logic with hash-based deduplication.
- Chatbot with voice and streaming response.
- Documentation detailing system design and usage.

---
