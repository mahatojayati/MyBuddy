import streamlit as st
from textblob import TextBlob
import google.generativeai as genai

# --- 1. CONFIGURATION & UI ---
st.set_page_config(page_title="Student Companion", page_icon="🌱")
st.title("🌱 Student Mental Health Companion")
st.caption("A safe space to talk, breathe, and find balance.")

# --- 2. SETUP & SECRETS ---
# Use the key name from your secrets.toml, not the raw key string!
try:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
except Exception:
    st.error("API Key not found. Please set GENAI_API_KEY in Streamlit Secrets.")

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a supportive student peer. Use a calming, empathetic tone. Keep responses short. If the user is in crisis, provide resources immediately."
)

# --- 3. UTILITIES ---
CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "hurt myself", "self-harm"]

def check_for_crisis(text):
    return any(keyword in text.lower() for keyword in CRISIS_KEYWORDS)

def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("Emergency Resources")
    st.error("🚨 If you are in immediate danger, contact emergency services.")
    st.markdown("[Find a Crisis Hotline](https://www.findahelpline.com/)")

# --- 6. CHAT DISPLAY ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- 7. THE SINGLE CHAT INPUT (The Fix) ---
if prompt := st.chat_input("How are you feeling today?"):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # A. Crisis Check
    if check_for_crisis(prompt):
        crisis_msg = "It sounds like you're going through a very difficult time. Please call 988 or 911 immediately."
        st.chat_message("assistant").error(crisis_msg)
        st.session_state.messages.append({"role": "assistant", "content": crisis_msg})
        st.stop()

    # B. Sentiment Analysis
    score = get_sentiment(prompt)
    prefix = ""
    if score < -0.6:
        prefix = "I can hear how much you're struggling. "
    elif score < 0:
        prefix = "It sounds like things are a bit heavy lately. "

    # C. Gemini Response
    with st.chat_message("assistant"):
        try:
            # Note: start_chat history should ideally map your session_state
            chat = model.start_chat(history=[]) 
            response = chat.send_message(prompt)
            full_response = f"{prefix}{response.text}"
            st.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error("I'm sorry, I can't discuss this. Please reach out to a professional.")
