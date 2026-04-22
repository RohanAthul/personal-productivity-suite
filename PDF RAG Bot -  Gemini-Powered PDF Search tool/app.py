import os
import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="PDF RAG Bot", page_icon="🤖")
st.title("Gemini with RAG")

# --- SIDEBAR: PDF UPLOAD ---
with st.sidebar:
    st.header("Upload Context")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    st.header("Model Settings")
    
    # Temp mapping Dict
    temp_options = {
        "Precise": 0.0,
        "Balanced": 0.5,
        "Creative": 1.0
    }

    # Creating the slider using the keys from the dictionary
    temp_label = st.select_slider(
        "Model Behavior",
        options=list(temp_options.keys()),
        value="Balanced"
    )

    # Mapping label back to float for LLM
    actual_temp_value = temp_options[temp_label]

st.write(f"The model is currently set to a temperature of: {actual_temp_value}")

# Extract text from PDF
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI: DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- UI: INPUT & RAG LOGIC ---
if prompt := st.chat_input("Ask about your document..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare Context
    context = ""
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            context = get_pdf_text(uploaded_file)
            # For a true RAG, you'd use a Vector DB here. 
            # For a simple version, we'll pass the most relevant text.
            context_prompt = f"Context from PDF:\n{context[:5000]}\n\nUser Question: {prompt}"
    else:
        context_prompt = prompt

    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Use streaming with the context-aware prompt
            for chunk in client.models.generate_content_stream(
                model="gemini-3-flash-preview",
                contents=context_prompt,
                config=types.GenerateContentConfig(temperature=actual_temp_value)
            ):
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error: {e}")
