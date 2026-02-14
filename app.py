import streamlit as st
import google.generativeai as genai
from textblob import TextBlob

# --- CONFIG & SECRETS ---
try:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
except Exception:
    st.error("Missing GENAI_API_KEY in Streamlit Secrets.")

# Initialize Model once - FIX FOR THE 404 ERROR
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", 
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
            prefix = get_sentiment_prefix(prompt)
            chat = model.start_chat(history=[]) 
            response = chat.send_message(prompt)
            
            # FIX FOR THE EXCEPTION CRASH 
            # If safety filters block the prompt, response.text doesn't exist.
            if response.candidates and response.candidates[0].content.parts:
                full_response = f"{prefix}{response.text}"
                st.write(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("I cannot discuss that specific topic due to safety constraints. How else can I help?")
                
        except Exception as e:
            st.error(f"API Error: {e}")
