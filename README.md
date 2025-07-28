# Periodic Crawler RAG System

![](https://img.shields.io/badge/status-proof--of--concept-blue) ![](https://img.shields.io/badge/language-Python3.11-green) ![](https://img.shields.io/badge/VectorDB-Weaviate-orange)

---

## Overview

The **Periodic Crawler Retrieval-Augmented Generation (RAG) System** is a proof-of-concept automated pipeline designed to:

- Crawl ecommerce websites periodically to fetch fresh product pages.
- Process and chunk product page content intelligently.
- Embed and index content chunks into a vector database (Weaviate) using OpenAI embeddings.
- Enable a voice-enabled and text-based chatbot interface that answers product-related queries with contextually relevant information retrieved from the latest crawled data.

This project demonstrates how to combine scalable web crawling, semantic vector search, and large language models (LLMs) such as OpenAI's GPT-3.5 to build a powerful product assistant.

---

## Key Features

- **Modular Periodic Crawling**: Asynchronous Selenium crawler respects `robots.txt`, parses sitemaps, and scrapes dynamic ecommerce page content.
- **Content Chunking & Deduplication**: Page text is chunked and hashed to prevent redundant indexing.
- **Semantic Vector Storage**: Uses Weaviate vector DB with OpenAI `text2vec-openai` embeddings.
- **Voice + Text Chatbot**: Streamlit app integrating Whisper for speech-to-text, GPT-3.5 for answer generation, and offline pyttsx3 for Text-to-Speech.
- **Automated Scheduling**: APScheduler based scheduler runs crawling and upsert pipelines every 30 minutes.
- **Dockerized Deployment**: Includes Dockerfile and docker-compose for containerized Weaviate and scheduler services.

---

## Repository Structure

```
.
├── app/
│   ├── chatbot/                # Streamlit chatbot frontend with voice and GPT integration
│   ├── crawler/                # Crawler modules: Selenium-based, sitemap, robots.txt helpers
│   ├── scheduler/              # Pipeline scheduler using APScheduler
│   ├── upsert/                 # Weaviate upsert and schema setup scripts
│   ├── utils/                  # Utility modules (hashing, UUID generation)
│   ├── test/                   # Test scripts for crawling, indexing, benchmark, voice & chatbot demos
│   └── visualize/              # Visualization scripts (e.g., TSNE plotting)
├── data/                       # Crawled data JSON files and URL lists
├── docs/                       # Research paper style documentation (project overview, methodology, etc.)
├── logs/                       # Log files including scheduler logs and crawl failures
├── weaviate-data/              # Persistent volume for Weaviate vector DB data
├── Dockerfile                  # Docker image definition for scheduler and crawler
├── docker-compose.yml          # Compose file to run Weaviate and scheduler containers
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- Docker and Docker-Compose
- OpenAI API Key (for embeddings and GPT chat)
- Environment variables setup in `.env` file or your shell environment:

```
OPENAI_API_KEY=your_openai_api_key
WEAVIATE_API_KEY=your_weaviate_api_key_or_empty_for_local
```

### Step 1: Clone and Install

```
git clone 
cd periodic-crawler-scrapping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Weaviate Vector DB with Docker Compose

```
docker-compose up -d weaviate
```

This will start Weaviate with OpenAI embedding module enabled.

### Step 3: Setup Weaviate Schema

```
python app/upsert/setup_schema.py
```

### Step 4: Run Scheduler (Starts periodic crawling + upsert)

```
python -m app.scheduler.scheduler
```

Alternatively, run the full pipeline manually:

```
python app/scripts/run_full_pipeline.py
```

### Step 5: Launch Chatbot Interface

```
streamlit run app/chatbot/chatbot.py
```

Open your browser at the URL shown by Streamlit (usually `http://localhost:8501`).

---

## Usage

- The scheduler automatically runs every 30 minutes by default, crawling the configured start URL(s), chunking content, and updating Weaviate.
- Users can interact with the chatbot via voice or text queries about products.
- The chatbot fetches relevant context from the vector DB and generates answers using GPT-3.5.
- Text-to-speech (TTS) answers are synthesized locally via pyttsx3.

---

## Customization

- Modify crawl start URLs, concurrency, and chunk size via environment variables or source code in `app/crawler/crawler_mp.py`.
- Extend the chatbot question answering logic in `app/chatbot/chatbot.py`.
- Add new crawler/test scripts in `app/test/` to compare scraping frameworks or voice/TTS engines.
- Update the scheduler interval or pipeline flow in `app/scheduler/scheduler.py`.

---

## Documentation

See the comprehensive research-style documentation in the `docs/` folder covering:

- Project overview and goals
- Problem statement and methodology
- Architecture and workflow diagrams
- Technical stack and analysis
- Experimentation, results, and future scope

---

## Tools & Technologies

- Python 3.11
- Selenium and Playwright for crawling
- BeautifulSoup, Scrapy for alternative scraping methods
- Weaviate vector database with OpenAI embeddings
- OpenAI GPT-3.5 Turbo for language generation
- OpenAI Whisper and pyttsx3 for speech recognition and synthesis
- Streamlit for chatbot user interface
- APScheduler for pipeline automation
- Docker & Docker Compose for containerized deployment

---

## Contributing

Contributions are welcome! Please open issues or pull requests for:

- Bug fixes or improvements
- New crawling or voice integration methods
- Enhanced chatbot features or UI
- Additional documentation or research content

---

## License

This project is provided as-is under the MIT License. See `LICENSE` file for details.

---

## Contact

For questions or support, contact:  
**Divyey Arora** - [divyey@gmail.com]

---

Thank you for exploring the Periodic Crawler RAG System!

---
