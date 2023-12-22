import os 
import json
from PIL import Image
import streamlit as st

import google.generativeai as genai

GEMINI_MODEL = "gemini-pro-vision"


def login(**kwargs):
    st.session_state["login"] = True
    st.session_state["GOOGLE_API_KEY"] = kwargs.pop("GOOGLE_API_KEY", "")
    st.session_state["OPENAI_API_KEY"] = kwargs.pop("OPENAI_API_KEY", "")

def login_page():
    st.title("Dixit Image")
    google_api_key = st.text_input("Set your Google API Key")
    openai_api_key = st.text_input("Set your OpenAI API Key")
    if st.button("Login"):
        if google_api_key or openai_api_key:
            st.write(f"Your GOOGLE_API_KEY is {google_api_key}")
            st.write(f"Your OPENAI_API_KEY is {openai_api_key}")
            login(GOOGLE_API_KEY=google_api_key, OPENAI_API_KEY=openai_api_key)
            st.rerun()
    
def main_page():
    
    st.title("Dixit Image")
    st.write("Dixit Image support you to title your image for now.")
    
    # Validation
    if st.session_state["GOOGLE_API_KEY"] != "":
        genai.configure(api_key=st.session_state["GOOGLE_API_KEY"])
    
    # Input Image
    uploaded_img = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_img is not None:
        st.session_state["img"] = uploaded_img
    
    if "img" in st.session_state:
        bytes_data = st.session_state["img"].getvalue()
        st.image(bytes_data, width=150)
        img = Image.open(st.session_state["img"])
        
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
            
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])
        
        
        if user_input := st.chat_input():
            user_msg = {
                "role": "user",
                "content": user_input
            }
            st.chat_message(user_msg["role"]).write(user_msg["content"])
            st.session_state["messages"].append(user_msg)
            
            model = genai.GenerativeModel(GEMINI_MODEL)
            input_prompt = json.dumps(st.session_state["messages"], ensure_ascii=False)
            response_gen = model.generate_content([input_prompt, img], stream=True)
            
            with st.chat_message("Bot"):
                msg_placeholder = st.empty()  
                for chunk in response_gen:
                    if isinstance(chunk, str):
                        msg_placeholder.markdown(chunk.text + "▌")

            full_response: str = chunk.text
            msg_placeholder.markdown(full_response)
            st.session_state["messages"].append({"role": "bot", "content": full_response})
    
    
if __name__ == "__main__":
    if not st.session_state.get("login", False):
        login_page()
    else: 
        main_page()