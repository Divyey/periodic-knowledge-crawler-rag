# 006 Workflow Diagram + Flowchart

## Overview

This section explains the detailed workflow of the Periodic Crawler RAG System using flowcharts and stepwise descriptions. It visually complements the methodology and architecture sections by illustrating how components interact during a typical pipeline run.

---

## Workflow Steps

1. **Scheduler Activation**  
   The scheduler triggers the crawl-upsert-chatbot cycle periodically (e.g., every 30 minutes).

2. **Sitemap Parsing & URL Collection**  
   The crawler fetches sitemaps from the target site and parses URLs, respecting robots.txt rules.

3. **Concurrent Page Crawling**  
   Multiple URLs are scraped in parallel using Selenium, loading dynamic page content.

4. **Content Extraction and Chunking**  
   Extracted page text is chunked into smaller pieces for downstream processing.

5. **Content Hashing and Deduplication**  
   Hashes are computed for each chunk to detect content changes across crawl runs.

6. **Upsert to Vector Database**  
   New or updated chunks are upserted to Weaviate, where OpenAI embeddings are generated and stored.

7. **Chatbot Query Handling**  
   When users ask questions, the chatbot queries Weaviate near-text search for relevant chunks.

8. **Answer Generation and Delivery**  
   The retrieved content is passed to OpenAI GPT-3.5 for answer generation, which is then presented via text or synthesized speech.

---

## Textual Flowchart Representation
```
┌─────────────────────────┐
│ Scheduler Trigger       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Fetch & Parse Sitemaps  │
│ + Check robots.txt      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Concurrent Page Crawl   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Extract & Chunk Content │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Compute Chunk Hashes    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Upsert to Weaviate      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Chatbot Query Loop      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Generate & Deliver      │
│ Answers (TTS)           │
└─────────────────────────┘
```
*This workflow diagram depicts the continuous operations bridging crawling, indexing, and conversational AI for end users.*
 
