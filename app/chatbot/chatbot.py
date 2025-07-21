import os
import streamlit as st
import logging
from dotenv import load_dotenv
from openai import OpenAI  # New-style OpenAI v1.x client!
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)

# --- Load OpenAI Key ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit Config ---
st.set_page_config(page_title="🛍️ Product Chatbot", layout="centered")
st.title("🌊🏄🏾‍♂️🌊 Product Chatbot")
st.caption("Ask questions about any product — powered by Weaviate + OpenAI")

# --- Weaviate Collection ---
@st.cache_resource
def get_weaviate_collection():
    client = WeaviateClient(
        connection_params=ConnectionParams.from_params(
            http_host="localhost",
            http_port=8080,
            grpc_host="localhost",
            grpc_port=50051,
            http_secure=False,
            grpc_secure=False,
        )
    )
    client.connect()
    return client.collections.get("PageChunk")

collection = get_weaviate_collection()

# --- OpenAI CLIENT ---
openai_client = OpenAI(api_key=openai_key)  # Pass key explicitly if not set globally

def query_weaviate_and_answer(question: str, top_k=7):
    response = collection.query.near_text(
        query=question,
        limit=top_k,
        return_properties=["content", "url", "last_updated"]
    )
    
    if not response.objects:
        return "❌ Sorry, I couldn’t find any relevant information in our product catalog.", []

    # Log retrieved chunk contents for debugging / verification
    logging.info("Retrieved Chunks:")
    for obj in response.objects:
        content_snippet = obj.properties.get("content", "")[:200].replace("\n", " ")
        logging.info(f"- URL: {obj.properties.get('url', '')}")
        logging.info(f"  Content snippet: {content_snippet}")

    context_snippets = []
    links = []

    for obj in response.objects[:2]:
        url = obj.properties.get("url", "")
        content = obj.properties.get("content", "").strip()
        links.append(url)
        context_snippets.append(f"[Source]({url}):\n{content}")

    context = "\n\n---\n".join(context_snippets)

    prompt = f"""You are a helpful product expert chatbot.

Your job is to answer customer questions **only using the product context below**, which is scraped directly from the site.

Prices are shown with the rupee symbol ₹ followed by the amount (e.g., ₹5,479.00). Please identify and reference prices accurately when answering.

🏷️ Context:
{context}

🧑🏻‍💬 User Question: {question}

🎯 Instructions:
- ONLY answer if relevant info is clearly found in the context (like price, size, offers).
- DO NOT make up answers or hallucinate unavailable products or prices.
- If no info is available, say: "Sorry, I couldn’t find any reliable info."
- Include at least one relevant product URL explicitly in your answer.

Answer:"""

    try:
        chat_completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise product assistant trained to respond ONLY using retrieved product website content."
                },
                {"role": "user", "content": prompt}
            ]
        )
        answer = chat_completion.choices[0].message.content.strip()
        return answer, links
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return f"⚠️ OpenAI Error: {e}", []

# --- Streamlit UI ---
with st.form("chat_form"):
    question = st.text_input(
        "Ask a question about our products (e.g. 'What's the price of the yellow kurta?')", ""
    )
    submitted = st.form_submit_button("Ask")

if submitted and question.strip():
    with st.spinner("Retrieving from vector DB + generating answer..."):
        final_response, source_links = query_weaviate_and_answer(question.strip())
        st.markdown("### ✅ Answer")
        st.write(final_response)

        if source_links:
            st.markdown("### 🔗 Source Links")
            for url in source_links:
                st.markdown(f"- [{url}]({url})")
