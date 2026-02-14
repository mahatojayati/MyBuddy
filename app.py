import streamlit as st
import google.generativeai as genai
from textblob import TextBlob

# --- CONFIG & SECRETS ---
try:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
except Exception:
    st.error("Missing GENAI_API_KEY in Streamlit Secrets.")

# --- MODEL INITIALIZATION ---
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are MyBuddy, an empathetic, conversational mental health companion for university students. "
        "Do not sound like a clinical therapist or a robot. Speak like a caring, emotionally intelligent friend. "
        "Use natural phrasing, occasional conversational fillers, and warm language. "
        "Reflect the user's emotions back to them to show understanding. "
        "Never give medical diagnoses. Keep responses concise (2-3 sentences max) to encourage back-and-forth dialogue."
    )
)

# --- CORE LOGIC FUNCTIONS ---
def get_sentiment_prefix(text):
    score = TextBlob(text).sentiment.polarity
    if score < -0.6:
        return "I can hear how much you're struggling right now. "
    elif score < 0:
        return "It sounds like things are a bit heavy lately. "
    return ""

# --- STATE MANAGEMENT ---
# THIS IS THE PART YOU DELETED. IT MUST BE ABOVE THE CHAT DISPLAY.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- CHAT INTERFACE ---
if prompt := st.chat_input("How are you feeling today?"):
    
    # 1. TRANSLATE HISTORY FOR GEMINI
    gemini_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # 2. UPDATE STREAMLIT UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3. GENERATE RESPONSE
    with st.chat_message("assistant"):
        try:
            prefix = get_sentiment_prefix(prompt)
            chat = model.start_chat(history=gemini_history) 
            response = chat.send_message(prompt)
            
            if response.candidates and response.candidates[0].content.parts:
                full_response = f"{prefix}{response.text}"
                st.write(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("I cannot discuss that specific topic due to safety constraints. How else can I help?")
                
        except Exception as e:
            st.error(f"API Error: {e}")
