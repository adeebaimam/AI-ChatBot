import streamlit as st
import requests
import speech_recognition as sr
from streamlit_lottie import st_lottie
import json
from gtts import gTTS
import os
import tempfile
import httpx

# Flask Backend URL
BACKEND_URL = "http://127.0.0.1:5000/chat"

# Load Lottie Animation
def load_lottie_animation(url: str = None):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

# Load animation
lottie_animation = load_lottie_animation("https://assets10.lottiefiles.com/packages/lf20_zw0djhar.json")

# Function to send messages to the backend
def get_response(user_message):
    try:
        response = requests.post(BACKEND_URL, json={"message": user_message})
        response.raise_for_status()
        return response.json().get("reply", "Sorry, I couldn't understand that.")
    except requests.Timeout:
        return "⚠️ Error: Server response took too long. Try again."
    except requests.RequestException:
        return "⚠️ Error: Unable to connect to the chatbot server."

# Function to capture speech input
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source) 
        audio = recognizer.listen(source, phrase_time_limit=10)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Error: Could not request results."

# Function to convert text to speech
def text_to_speech(text):
    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        
    except Exception:
        st.error("Error in Text-to-Speech conversion.")

# Streamlit UI
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Custom Styling
st.markdown(
    """
    <style>
        body {
            background-color: #000000;
            color: white;
        }
        .chat-container {
            max-width: 700px;
            margin: auto;
        }
        .chat-bubble-user, .chat-bubble-bot {
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 10px;
            max-width: 70%;
            font-size: 16px;
            line-height: 1.4;
            background-color: #000000;
            color: white;
        }
        .chat-bubble-user {
            align-self: flex-end;
            text-align: right;
        }
        .chat-bubble-bot {
            align-self: flex-start;
            text-align: left;
        }
        .chat-container div {
            display: flex;
            flex-direction: column;
        }
        input {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: none;
            background-color: #000000;
            color: white;
        }
        button {
            padding: 10px 15px;
            border-radius: 10px;
            border: none;
            background-color: #1E88E5;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #1565C0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 AI Chatbot")
st.write("Chat with an AI-powered assistant!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat Display
chat_container = st.container()

with chat_container:
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">🧑‍💻 {chat["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot">🤖 {chat["message"]}</div>', unsafe_allow_html=True)

# Chat Input
user_input = st.text_input("Type your message:", key="user_input", placeholder="Say something...", on_change=lambda: st.session_state.submit_chat(), args=())

if "submit_chat" not in st.session_state:
    def submit_chat():
        if st.session_state.user_input:
            bot_response = get_response(st.session_state.user_input)
            st.session_state.chat_history.append({"role": "user", "message": st.session_state.user_input})
            st.session_state.chat_history.append({"role": "bot", "message": bot_response})
            text_to_speech(bot_response)
            st.session_state.user_input = ""
            
    st.session_state.submit_chat = submit_chat

st.button("📩 Send", on_click=st.session_state.submit_chat)

# Speech Input
if st.button("🎤 Speak", key="voice_input"):
    user_voice_input = speech_to_text()
    if user_voice_input:
        st.session_state.chat_history.append({"role": "user", "message": user_voice_input})
        bot_response = get_response(user_voice_input)
        st.session_state.chat_history.append({"role": "bot", "message": bot_response})
        text_to_speech(bot_response)
        st.rerun()

# Display Lottie Animation
if lottie_animation:
    st_lottie(lottie_animation, height=100, width=100, key="loading")
