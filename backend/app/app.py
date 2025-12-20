import streamlit as st
from summarizer_logic import generate_summary

# --- Page Configuration ---
st.set_page_config(
    page_title="SmartSum with Groq",
    page_icon="📝",
    layout="centered"
)

# --- Custom CSS for styling ---
st.markdown("""
    <style>
    .stTextArea textarea {font-size: 16px;}
    .stButton button {background-color: #ff4b4b; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: API Key Setup ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
st.sidebar.markdown("[Get your Groq API Key here](https://console.groq.com/keys)")

st.sidebar.info("Note: Your API key is not stored permanently.")

# --- Main App Interface ---
st.title("📝 SmartSum: Context-Aware Summarizer")
st.write("Summarize long articles instantly using the speed of Groq AI.")

# 1. Input Text
text_input = st.text_area("Paste your article or text here:", height=250)

# 2. Select Mode
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("Select Summary Mode:", ["General Summary", "Keyword-Focused Summary"])

keyword = ""
if mode == "Keyword-Focused Summary":
    with col2:
        keyword = st.text_input("Enter the specific Keyword/Topic:")
        if not keyword:
            st.warning("Please enter a keyword to focus on.")

# 3. Generate Button
if st.button("Generate Summary"):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar to proceed.")
    elif not text_input:
        st.error("Please provide some text to summarize.")
    else:
        # Show loading spinner while fetching data
        with st.spinner("Analyzing text with Groq AI..."):
            
            # Map UI selection to backend logic
            backend_mode = "keyword" if mode == "Keyword-Focused Summary" else "general"
            
            # Call the function
            summary_result = generate_summary(
                text=text_input, 
                api_key=api_key, 
                mode=backend_mode, 
                keyword=keyword
            )
            
            # Display Result
            st.success("Summary Generated Successfully!")
            st.markdown("### 📄 Summary Result")
            st.markdown(f">{summary_result}")
            
            # Copy Button Logic (Streamlit helper)
            st.code(summary_result, language=None)

# --- Footer ---
st.markdown("---")
st.markdown("Powered by **Groq API** & **Streamlit**")