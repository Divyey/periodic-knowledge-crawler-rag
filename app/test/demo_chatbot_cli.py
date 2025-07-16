import os
import re
from dotenv import load_dotenv
import streamlit as st
import weaviate
from weaviate.classes.init import Auth

# Optional fallback
try:
    import openai
except ImportError:
    openai = None

# 🔐 Load from .env
load_dotenv()

# ENV VARS
WEAVIATE_URL = os.getenv("WEAVIATE_CLUSTER_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION = os.getenv("WEAVIATE_COLLECTION", "PageChunk")

# 🔌 Connect to Weaviate
def connect():
    if "weaviate_client" not in st.session_state:
        st.session_state.weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY) if WEAVIATE_API_KEY else None,
            headers={"X-OpenAI-Api-Key": OPENAI_API_KEY} if OPENAI_API_KEY else None,
            skip_init_checks=True
        )
    return st.session_state.weaviate_client

# 🔍 Search vector DB from single product page
def search_chunks(query, top_k: int = 3):
    client = connect()
    collection = client.collections.get(COLLECTION)
    results = collection.query.near_text(
        query=query,
        limit=top_k,
        return_properties=["url", "content", "chunk_id", "last_updated"]
    )
    unique_results = {}
    for obj in results.objects:
        cid = obj.properties.get("chunk_id")
        if cid and cid not in unique_results:
            unique_results[cid] = obj
    return list(unique_results.values())

# 💬 Answer using OpenAI GPT
def generate_answer(chunks, question):
    if not openai or not OPENAI_API_KEY:
        return "OpenAI API key not set."

    context = "\n\n".join([c.properties.get('content', '') for c in chunks])

    prompt = f"""
You are a helpful product assistant. Use the following context to answer the user's question.

Instructions:
- Only use data from the context below.
- If context has ₹ price, return it.
- Mention available sizes if found (like S, M, L).
- If you can’t confidently answer, say "Sorry, I don’t have that information."

Context:
{context}

Question: {question}

Answer:
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {e}"

# Parse price if tagged
def extract_price(text):
    match = re.search(r"(₹\s?\d+[,\d]*\.?\d*|Rs\.?\s?\d+[,\d]*\.?\d*)", text, re.IGNORECASE)
    return match.group(0) if match else text

# 🖼️ UI
st.set_page_config(page_title="Single Product Q&A", page_icon="🧠")
st.title("🧠 Ask a Question About This Product")
st.caption("Uses the most recent upserted content from 1 page")

query = st.chat_input("Ask a product question...")

if query:
    with st.spinner("Retrieving product data..."):
        chunks = search_chunks(query, top_k=3)

    with st.spinner("🔍 Thinking..."):
        if not chunks:
            answer = "Sorry, no product information found."
        else:
            answer = generate_answer(chunks, query)
            if any(word in query.lower() for word in ["price", "cost", "₹", "rs", "how much"]):
                answer = extract_price(answer)

    # 🤖 Output
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        st.markdown(answer)

    # 🧾 View reference content
    with st.expander("🔍 View context used"):
        for i, chunk in enumerate(chunks, 1):
            props = chunk.properties
            st.write(f"**Result {i}**")
            st.markdown(f"- 📄 **URL**: {props.get('url')}")
            st.markdown(f"- 🔹 **Chunk ID:** {props.get('chunk_id')}")
            st.markdown(f"- 🕒 **Last updated:** {props.get('last_updated')}")
            st.text(props.get('content', '')[:1000])
            st.markdown("---")
