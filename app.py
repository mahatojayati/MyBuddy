import streamlit as st
import google.generativeai as genai
from textblob import TextBlob

# --- CONFIG & SECRETS ---
# Ensure your .streamlit/secrets.toml has: GENAI_API_KEY = "your_key_here"
try:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
except Exception:
    st.error("Missing GENAI_API_KEY in Streamlit Secrets.")

# Initialize Model once
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a supportive student peer. Use a calming tone. Keep it brief."
)

# --- CORE LOGIC FUNCTIONS ---
def get_sentiment_prefix(text):
    score = TextBlob(text).sentiment.polarity
    if score < -0.6:
        return "I can hear how much you're struggling right now. "
    elif score < 0:
        return "It sounds like things are a bit heavy lately. "
    return ""

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Single Chat Input
if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # 1. Generate Sentiment Prefix
            prefix = get_sentiment_prefix(prompt)
            
            # 2. Get AI Response
            # We use a fresh chat session for now to keep it simple
            chat = model.start_chat(history=[]) 
            response = chat.send_message(prompt)
            
            # 3. Combine and Display
            full_response = f"{prefix}{response.text}"
            st.write(full_response)
            
            # 4. Save to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # CRITICAL: This shows you the ACTUAL error in the UI so you can fix it
            st.error(f"API Error: {e}") 
            st.info("Please check your API quota or safety filters.")
