# 004 Methodology

## Overview

The methodology consists of a multi-stage pipeline combining asynchronous web crawling, vector database ingestion, and generative AI-backed chat.

### 1. Web Crawling

- Uses Selenium for headless browsing to render dynamic ecommerce pages.
- Extracts URLs from sitemaps obtained via robots.txt or common paths.
- Filters URLs based on crawling policies in robots.txt.
- Concurrent scraping with asyncio and semaphore limits.

### 2. Content Chunking & Hashing

- Extract page textual content from `<body>` tag.
- Chunk text into fixed-size segments (default ~1000 chars).
- Compute SHA-256 hash per chunk to detect content changes over time.

### 3. Vector Storage & Upsert

- Use Weaviate vector database with OpenAI textual embeddings.
- Leverage chunk IDs and hashes for upsert logic.
- Insert new chunks, replace updated ones, skip unchanged chunks.

### 4. Chatbot Frontend

- Streamlit app supporting:
  - Text input with chat history.
  - Voice recording with Whisper-based transcription.
  - TTS output using pyttsx3 for answers.
- Queries trigger semantic search over indexed chunks using Weaviate near-text search.
- OpenAI GPT-3.5 model generates final responses from retrieved context.

---

## Diagram Placeholder
```
┌────────────────────────────┐
│     Scheduled Trigger      │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│   Create URL Frontier      │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│     Fetch Next URL         │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│  Find robots.txt File      │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ robots.txt Allows Fetch?   │
└──────┬──────────┬──────────┘
   Yes │          │ No
       ▼          ▼
┌─────────────┐ ┌───────────────────────┐
│ Fetch and   │ │  Skip and Fetch Next  │
│ Normalize   │ └───────────────────────┘
│ Page        │
└──────┬──────┘
       │
       ▼
┌────────────────────────────┐
│    Parsed Before?          │
└──────┬─────────┬───────────┘
   Yes │         │ No
       ▼         ▼
┌─────────────┐ ┌─────────────────────┐
│ Skip Page   │ │ Parse Page Content  │
└─────────────┘ └─────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────────┐
                 │ Store Page Chunks   │
                 └─────────┬───────────┘
                           │
                           ▼
                 ┌───────────────────────────┐
                 │ Extract URLs & Add to      │
                 │     Frontier               │
                 └───────────────────────────┘

```
#Methodology Steps

Periodic Trigger: Scheduler initiates the crawl pipeline at regular intervals (e.g., every 30 minutes).

URL Management: Start with the URL frontier; manage discovered and pending URLs.

robots.txt Compliance: Before each page fetch, check robots.txt for crawl permissions.

Page Fetching: Use Selenium (headless browser) to load and render dynamic pages.

De-duplication: Check if page content was already parsed by comparing normalized hashes.

Content Chunking: Break page body text into fixed-size chunks for index/storage.

Semantic Upsert: Insert or update content chunks in a vector database (Weaviate) with OpenAI embeddings.

Link Extraction: Extract additional links from parsed pages and add uncrawled ones to the URL frontier.

Repeat: Continue until crawl frontier is empty; system awaits next scheduled trigger.

---