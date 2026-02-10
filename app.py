import streamlit as st
from textblob import TextBlob
import google.generativeai as genai

# 1. Setup Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Use 'gemini-1.5-flash' for speed/cost or 'pro' for deeper empathy
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a supportive student peer. Use a calming, empathetic tone. Keep responses short. If the user is in crisis, provide resources immediately."
)

# 2. Safety Settings (The CSE 'Guardrail' approach)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

# 3. Chat Logic
if prompt := st.chat_input("What's on your mind?"):
    st.chat_message("user").write(prompt)
    
    # Start or continue a chat session with history
    chat = model.start_chat(history=[])
    
    try:
        response = chat.send_message(prompt, safety_settings=safety_settings)
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error("I'm sorry, I can't discuss this topic. Please reach out to a professional if you're feeling distressed.")

# --- CONFIGURATION & UI ---
st.set_page_config(page_title="Student Companion", page_icon="🌱")
st.title("🌱 Student Mental Health Companion")
st.caption("A safe space to talk, breathe, and find balance.")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.header("Emergency Resources")
    st.error("🚨 If you are in immediate danger, please contact local emergency services or a campus counselor.")
    st.markdown("[Find a Crisis Hotline](https://www.findahelpline.com/)")
    
    st.divider()
    st.subheader("Quick Relaxation")
    if st.button("4-7-8 Breathing Technique"):
        st.info("Inhale for 4s | Hold for 7s | Exhale for 8s")

# --- CORE LOGIC ---
def get_sentiment(text):
    analysis = TextBlob(text)
    # Returns a value between -1 (Negative) and 1 (Positive)
    return analysis.sentiment.polarity

# Display Chat History
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 1. Analyze Sentiment
    score = get_sentiment(prompt)
    
    # 2. Safety & Branching Logic
    if score < -0.6:
        response_prefix = "I can hear how much you're struggling right now. Please know you're not alone. "
    elif score < 0:
        response_prefix = "It sounds like things are a bit heavy lately. "
    else:
        response_prefix = ""
        
        response = llm.invoke(messages)
        full_response = f"{response_prefix}{response.content}"
        st.write(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    


# --- SAFETY CONFIGURATION ---
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "hurt myself", 
    "self-harm", "cutting", "overdose", "don't want to live"
]

def check_for_crisis(text):
    """Returns True if any crisis keyword is found in the user input."""
    text = text.lower()
    return any(keyword in text for keyword in CRISIS_KEYWORDS)

# --- UPDATED CHAT LOOP ---
if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 1. IMMEDIATE SAFETY CHECK (Hard Intercept)
    if check_for_crisis(prompt):
        with st.chat_message("assistant"):
            st.error("### I'm concerned about you.")
            st.write("It sounds like you're going through a very difficult time. I am an AI, and I cannot provide the professional help you deserve right now.")
            st.markdown("""
            **Please reach out to someone who can help:**
            * **National Suicide Prevention Lifeline:** Call or Text **988**
            * **Crisis Text Line:** Text **HOME** to **741741**
            * **Campus Security / Emergency:** Call **911**
            """)
            st.info("I am pausing our chat for a moment. Your safety is the priority.")
        
        # We append to history but stop execution here to prevent AI response
        st.session_state.messages.append({"role": "assistant", "content": "CRISIS_TRIGGERED: Resources Provided."})
        st.stop() # This stops Streamlit from running the rest of the script

    # 2. IF SAFE: Proceed to Sentiment & LLM Logic...
    # (Rest of your previous code goes here)
