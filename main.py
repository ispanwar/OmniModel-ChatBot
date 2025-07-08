import os
import json

import streamlit as st
import requests
# from dotenv import load_dotenv
# load_dotenv()
# configuring openai key
# working_dir = os.path.dirname(os.path.abspath(__file__))
# config_data = json.load(open(f"{working_dir}/config.json"))

# print(config_data)

# OPENROUTER_API_KEY = config_data["OPENROUTER_API_KEY"]
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_KEY = st.secrets["openrouter"]["api_key"]
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please set it in the .env file or config.json.")
# openai.api_key = OPENROUTER_API_KEY
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADER = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}


# setting streamlit

st.set_page_config(
    page_title="OmniModel Chatbot",
    page_icon="💬",
    layout="centered"
)

# initializing the chat if not present

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    

st.title("🗿 OmniModel Chatbot")
model_options = {
    # "GPT-4o (OpenAI)": "openai/gpt-4o",
    # "Claude 4 Sonnet (Anthropic)": "anthropic/claude-sonnet-4",
    "DeepSeek": "deepseek/deepseek-chat-v3-0324:free",
    "Google Gemini": "google/gemini-2.0-flash-exp:free",
    "Meta Llama 4": "meta-llama/llama-4-maverick:free",
    # "Gemini Pro (Google)": "google/gemini-2.0-flash-001",
    "Cypher-alpha": "openrouter/cypher-alpha:free",
    "Mistral-nemo": "mistralai/mistral-nemo:free",
    "Qwen": "qwen/qwq-32b:free"
    
}
selected_model_label = st.selectbox("Choose a model:",list(model_options.keys()), index=0)
selected_model = model_options[selected_model_label]
max_tokens_map = {
    # "openai/gpt-4o": 1916,                   # Context: 128k, but free-tier is ~4k-8k
    # "anthropic/claude-sonnet-4": 1618,       # Context: 200k, but free-tier practical ~4k
    "deepseek/deepseek-chat-v3-0324:free": 4000, # DeepSeek supports up to 32k, but free API likely 4k-8k
    "meta-llama/llama-4-maverick:free": 4000,    # Llama-4 supports 128k, free API typically ≤ 4k-8k
    "google/gemini-2.0-flash-exp:free": 4000, # Gemini Flash supports up to 2M, but free API is limited to ~4k-8k
    # "google/gemini-2.0-flash-001": 4000,     # Gemini Pro/Flash: up to 2M, but limit for most users ~4k-8k
    "openrouter/cypher-alpha:free": 4000,    # No public docs, but safe 4k
    "google/gemma-3n-e4b-it:free": 4000,     # Gemma's max is higher, but practical 4k
}
max_toks = max_tokens_map.get(selected_model, 4000)
# displaying the chat_history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# input field
user_prompt = st.chat_input(f"Ask anything to {selected_model_label}...")

if user_prompt:
    # add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role":"user","content":user_prompt})
    
    # send user's message to gpt4o and get a response
    payload = {
        "model": selected_model,
        "messages": [{"role": "system", "content": "You are a knowledgeable, friendly, and supportive AI tutor. Explain concepts in simple language, break down problems step-by-step, and provide real-world examples. Always encourage the user, and if you are unsure of an answer, be honest and suggest next steps."}, *st.session_state.chat_history],
        "max_tokens": max_toks,
    }
    try:
        response = requests.post(OPENROUTER_URL,headers=HEADER, json=payload)
        data = response.json()
        # st.write("Raw response: ",data)
        assistance_response = data["choices"][0]["message"]["content"]
    except Exception as e:
        assistance_response = f"An error occurred: {str(e)}"
    
    st.session_state.chat_history.append({"role":"assistant","content":assistance_response})
    
    # display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(assistance_response)
