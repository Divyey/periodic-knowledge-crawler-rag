# 008 Tech Stack Used

## Overview

This section lists the main technologies, tools, and frameworks used to build the Periodic Crawler RAG System Prototype, along with their roles.

---

### Backend

- **Python 3.11**: Core programming language for all modules.
- **Asyncio**: For concurrency in crawling.
- **Selenium (Chromedriver)**: Headless browser for scraping dynamic pages.
- **APScheduler**: For periodic pipeline orchestration.
- **HTTPX**: Async HTTP client for sitemap and robots.txt fetching.
- **BeautifulSoup (bs4)**: HTML/XML parsing of sitemaps and pages.
- **Webdriver Manager**: Automated ChromeDriver installation.

### Vector Database

- **Weaviate (v1.26.2)**: Vector search engine for storage and semantic retrieval.
- **OpenAI text2vec-openai Vectorizer**: Embedding model for vectorization of content chunks.
- **Docker**: Containerized deployment of Weaviate.

### AI / NLP Components

- **OpenAI GPT-3.5-turbo**: Chat completion and answer generation.
- **OpenAI Whisper**: Speech-to-text transcription.
- **pyttsx3**: Offline Text-to-Speech engine.

### Frontend / UI

- **Streamlit**: Web-based chat interface supporting voice and text.

### Utilities & Others

- **UUID**, **Hashlib**: For chunk identification and deduplication.
- **TQDM**: Progress bars during upsert and crawling.
- **Dotenv**: Load environment variables (`.env` files).

---

### Development & Deployment

- **Dockerfile + docker-compose.yml**: For container orchestration of Weaviate and scheduler.
- **VSCode / Any IDE**: Recommended for Python development.
- **Git**: Version control.

---

### Summary Chart

| Category       | Tools / Libraries                      |
|----------------|--------------------------------------|
| Language       | Python 3.11                          |
| Crawling       | Selenium, asyncio, HTTPX, BeautifulSoup |
| Scheduling     | APScheduler                         |
| Vector DB      | Weaviate (Docker)                   |
| AI / Models    | OpenAI GPT-3.5, Whisper, text2vec-openai |
| Frontend       | Streamlit                          |
| Deployment     | Docker, docker-compose              |
| Utilities      | TQDM, dotenv, hashlib, uuid          |

---

All external API keys (e.g., OpenAI) are loaded using environment variables via `python-dotenv`.

