import os
import streamlit as st
import logging
import whisper
import sounddevice as sd
import scipy.io.wavfile as wavfile
import tempfile
import pyttsx3
import re

from dotenv import load_dotenv
from openai import OpenAI
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

# Initialize logging and keys
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO)

# Initialize pyttsx3 TTS
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 155)

# ---- TTS Functions ----
def speak_answer(text):
    try:
        stripped = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        stripped = re.sub(r'http\S+', '', stripped)
        tts_engine.say(stripped.strip())
        tts_engine.runAndWait()
    except Exception as e:
        st.warning("TTS error: " + str(e))

def stop_tts():
    try:
        tts_engine.stop()
    except Exception as e:
        st.warning("Could not stop speech: " + str(e))

# ---- Whisper Recorder ----
def record_with_whisper(duration=5, model_size="base"):
    fs = 16000
    try:
        st.toast("🎙 Recording...", icon="🎤")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
        sd.wait()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wavfile.write(f.name, fs, audio)
            model = whisper.load_model(model_size)
            result = model.transcribe(f.name)
            return result["text"]
    except Exception as e:
        st.error("Audio error: " + str(e))
        return ""

# ---- Weaviate + OpenAI Clients ---
@st.cache_resource
def get_collection():
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

collection = get_collection()
openai_client = OpenAI(api_key=openai_key)

# ---- Answer Generation ----
def answer_from_knowledge(question, top_k=7):
    response = collection.query.near_text(
        query=question,
        limit=top_k,
        return_properties=["content", "url", "last_updated"]
    )
    if not response.objects:
        return "❌ No product information found.", []

    context_snippets, links = [], []
    for obj in response.objects[:2]:
        url = obj.properties.get("url", "")
        content = obj.properties.get("content", "").strip()
        links.append(url)
        context_snippets.append(f"[Source]({url}):\n{content}")

    context = "\n\n---\n".join(context_snippets)

    messages = [
        {"role": "system", "content": "Answer strictly using the ecommerce product context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
    ]

    try:
        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
        )
        final = res.choices[0].message.content.strip()
        return final, links
    except Exception as e:
        st.error("OpenAI error: " + str(e))
        return "⚠️ GPT error", []

# ---- Session State Init ----
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "typed_question" not in st.session_state:
    st.session_state.typed_question = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# ---- Keyboard Submit Handler ----
def on_key_enter():
    query = st.session_state.typed_question.strip()
    if query:
        with st.spinner("Thinking..."):
            answer, urls = answer_from_knowledge(query)
        st.session_state.chat_log.append({
            "question": query,
            "answer": answer,
            "links": urls,
            "voice": False
        })
        st.session_state.last_response = answer
        speak_answer(answer)
        st.session_state.typed_question = ""
        st.rerun()

# ---- Display Chat Log ----
st.set_page_config(page_title="🛍️ Voice Chatbot", layout="wide")
st.title("🧠 Smart Shopping Assistant (Voice + Chat)")
for msg in st.session_state.chat_log:
    with st.chat_message("user", avatar="🎙️" if msg["voice"] else "🧑‍💻"):
        st.markdown(msg["question"])
    with st.chat_message("ai", avatar="🤖"):
        st.markdown(msg["answer"])
        if msg["links"]:
            st.markdown("🔗 Product Links:")
            for l in msg["links"]:
                st.markdown(f"- [{l}]({l})")

# ---- Input + Mic + Controls --- (Bottom)
st.markdown("---")
input_col1, input_col2, input_col3 = st.columns([5, 1, 1])

with input_col1:
    st.text_input(
        "Ask about a product...",
        key="typed_question",
        label_visibility="collapsed",
        on_change=on_key_enter
    )

with input_col2:
    if st.button("🎤", use_container_width=True):
        transcript = record_with_whisper()
        if transcript:
            st.success(f"🗣️ You said: {transcript}")
            with st.spinner("Answering..."):
                reply, product_links = answer_from_knowledge(transcript)
            st.session_state.chat_log.append({
                "question": transcript,
                "answer": reply,
                "links": product_links,
                "voice": True
            })
            st.session_state.last_response = reply
            speak_answer(reply)
            st.rerun()

with input_col3:
    if st.button("⏹ Stop", use_container_width=True):
        stop_tts()
