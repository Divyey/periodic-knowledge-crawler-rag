# 001 Project Overview

## Introduction

The Periodic Crawler Retrieval-Augmented Generation (RAG) System is designed as a proof-of-concept (PoC) for building an automated pipeline that crawls ecommerce websites, processes and indexes product content, and supports an intelligent chatbot interface for answering user queries by leveraging large language models (LLMs) with up-to-date knowledge retrieval.

## Key Features

- **Periodic Web Crawling:** Uses Selenium and async Python to scrape and chunk ecommerce product pages.
- **Content Vectorization & Storage:** Upserts processed content into Weaviate vector database with OpenAI embeddings.
- **Voice & Text Chatbot:** Streamlit interface integrating Whisper for speech recognition and OpenAI GPT-3.5 for response generation.
- **Pipeline Automation:** Scheduler to run the full crawl-index-chat loop at configurable intervals.
- **Modular Design:** Decoupled components for crawling, upserting, chat logic, and scheduling.

## Motivation

Ecommerce platforms often lack intelligent assistants that can answer detailed product questions dynamically. This system aims to demonstrate how RAG architectures can close that gap by combining web crawling, semantic search, and powerful LLMs.

---
