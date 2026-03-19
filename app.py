import streamlit as st
import requests
import uuid
import datetime
import json
import os
import time

# -------------------------
# PAGE SETUP
# -------------------------
st.set_page_config(page_title="My AI Chat", layout="wide")
st.title("My AI Chat")

# -------------------------
# LOAD TOKEN
# -------------------------
hf_token = st.secrets.get("HF_TOKEN")

if not hf_token:
    st.error("Missing Hugging Face token")
    st.stop()

# -------------------------
# MEMORY FUNCTIONS
# -------------------------
def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            return json.load(f)
    return {}

def save_memory(new_data):
    memory = load_memory()
    memory.update(new_data)
    with open("memory.json", "w") as f:
        json.dump(memory, f)

# -------------------------
# SAVE CHAT
# -------------------------
def save_chat(chat_id, chat_data):
    os.makedirs("chats", exist_ok=True)
    with open(f"chats/{chat_id}.json", "w") as f:
        json.dump(chat_data, f)

# -------------------------
# SESSION STATE INIT
# -------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {}

# LOAD EXISTING CHATS
if not st.session_state.chats:
    if os.path.exists("chats"):
        for file in os.listdir("chats"):
            with open(f"chats/{file}", "r") as f:
                data = json.load(f)
                chat_id = file.replace(".json", "")
                st.session_state.chats[chat_id] = data

# CREATE FIRST CHAT IF EMPTY
if "current_chat" not in st.session_state or not st.session_state.chats:
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "timestamp": str(datetime.datetime.now())
    }
    st.session_state.current_chat = chat_id

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Chats")

if st.sidebar.button("➕ New Chat"):
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "timestamp": str(datetime.datetime.now())
    }
    st.session_state.current_chat = chat_id

# CHAT LIST
for chat_id, chat_data in list(st.session_state.chats.items()):
    col1, col2 = st.sidebar.columns([4, 1])

    if col1.button(chat_data["title"], key=chat_id):
        st.session_state.current_chat = chat_id

    if col2.button("✕", key=f"del_{chat_id}"):
        if os.path.exists(f"chats/{chat_id}.json"):
            os.remove(f"chats/{chat_id}.json")

        del st.session_state.chats[chat_id]

        if st.session_state.chats:
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
        else:
            st.session_state.current_chat = None

        st.rerun()

# -------------------------
# MEMORY SIDEBAR
# -------------------------
st.sidebar.markdown("## 🧠 User Memory")

memory = load_memory()
st.sidebar.json(memory)

if st.sidebar.button("Clear Memory"):
    with open("memory.json", "w") as f:
        json.dump({}, f)
    st.rerun()

# -------------------------
# ACTIVE CHAT
# -------------------------
if not st.session_state.current_chat:
    st.stop()

chat = st.session_state.chats[st.session_state.current_chat]

# -------------------------
# DISPLAY MESSAGES
# -------------------------
for msg in chat["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# CHAT INPUT
# -------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    try:
        headers = {"Authorization": f"Bearer {hf_token}"}

        # LOAD MEMORY INTO PROMPT
        memory = load_memory()
        system_message = {
            "role": "system",
            "content": f"Here is what you know about the user: {memory}"
        }

        payload = {
            "model": "meta-llama/Llama-3.2-1B-Instruct",
            "messages": [system_message] + chat["messages"],
            "max_tokens": 200
        }

        # STREAMING RESPONSE
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json={**payload, "stream": True},
            stream=True
        )

        full_reply = ""
        placeholder = st.empty()

        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")

                if decoded.startswith("data: "):
                    chunk = decoded.replace("data: ", "").strip()

                    if chunk == "[DONE]":
                        break

                    try:
                        data = json.loads(chunk)
                        token = data["choices"][0]["delta"].get("content", "")

                        full_reply += token
                        placeholder.markdown(full_reply)
                        time.sleep(0.02)

                    except:
                        pass

        # SAVE RESPONSE
        chat["messages"].append({
            "role": "assistant",
            "content": full_reply
        })

        save_chat(st.session_state.current_chat, chat)

        # -------------------------
        # MEMORY EXTRACTION
        # -------------------------
        extract_prompt = f"""
Extract any personal facts or preferences from this message.
Return ONLY JSON.

Message: {user_input}
"""

        extract_payload = {
            "model": "meta-llama/Llama-3.2-1B-Instruct",
            "messages": [{"role": "user", "content": extract_prompt}],
            "max_tokens": 100
        }

        extract_response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            headers=headers,
            json=extract_payload
        )

        extract_data = extract_response.json()

        try:
            extracted = extract_data["choices"][0]["message"]["content"]
            parsed = json.loads(extracted)
            if isinstance(parsed, dict):
                save_memory(parsed)
        except:
            pass

    except Exception as e:
        st.error(f"Error: {e}")