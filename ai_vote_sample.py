from pathlib import Path
import streamlit as st
import json
import requests
import numpy as np
from PIL import Image
import base64

import logging
from logging import config

import google.generativeai as genai

LOG_CONFIG_PATH = "./logging_config.ini"
config.fileConfig(LOG_CONFIG_PATH)
logger = logging.getLogger()


SUPPORTED_MODELS = [
    "gemini",
    "gpt4",
    "clip"
]
GEMINI_PROMPT = """
以下のタイトルとこの画像の関連度のスコアを0~1の間で予測してください．出力は小数点第2位まで表示し，数値のみを出力してください．Ex. 0.75
タイトル: {}

出力:
"""

st.title("Dixit Image")
images = list(Path("images").glob("*.png"))

def encode_img(img_path: str) -> str:
    """Encode image path to base64 string.

    Args:
        img_path (str): Image path.

    Returns:
        str: Base64 string.
    """
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_gemini_api(prompt: str, image: Image.Image, model_name: str = "gemini-pro-vision") -> float:
    """Call Gemini-Pro-vision API.

    Args:
        prompt (str): Prompt to predict similarity score.
        image (Image.Image): Image to predict the similarity score compared with given the title..
    """
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([prompt, image])
    logger.debug(f"response: {response}")
    
    try:
        score = float(response.text)
    except:
        raise ValueError("Response is not float.")
    
    return score


def call_gpt4_api(prompt: str, image: Image.Image, api_key: str, model_name: str = "gpt-4-vision-preview") -> float:
    base64_img = encode_img(image)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
    logger.debug(f"response: {response}")
    score = response["choices"][0]["message"]["content"]
    try:
        score = float(score)
    except:
        raise ValueError("Response is not float.")  
    return score
    

def select_page():
    st.title("Select Image")
    grid_width = 5
    # 画像をグリッド状に表示
    cols = st.columns(grid_width)

    check_states = [False] * len(images)
    for i, img in enumerate(images):
        with cols[i % grid_width]:
            st.image(str(img), use_column_width=True)
            check_states[i] = st.checkbox("Check", key=img)
            
    logger.info(f"check_states: {check_states}")

    if sum(check_states) == 4:
        logger.info("4枚選択されました。")
        if st.button("Submit"):
            logger.info("Submitボタンが押されました。")
        st.session_state["IsSelected"] = True
        st.session_state["selected_images"] = [img for img, state in zip(images, check_states) if state]

def setting_page():
    st.title("Setting")
    st.write("Setting Page")
    
    # モデルの選択
    model = st.radio(
        "Select Model",
        SUPPORTED_MODELS,
        index=0  # default: gemini
    )
    st.write(f"Selected Model: {model}")
    
    # モデルのパラメータ
    if model == "gemini":
        api_key = st.text_input("Set your Google API Key")
    elif model == "gpt4":
        api_key = st.text_input("Set your OpenAI API Key")
    elif model == "clip":
        pass
    else:
        raise NotImplementedError
    
    if st.button("Setting Complete"):
        st.session_state["model"] = model
        st.session_state["api_key"] = api_key
        st.session_state["setting"] = True
        st.rerun()
        
def main_page():
    st.title("Vote")
    if st.session_state["api_key"] == "":
        st.write(f"Please set your {st.session_state['model']} API Key")
        if st.button("Back to Setting"):
            st.session_state["setting"] = False
            st.rerun()
    
    if st.session_state["model"] == "gemini":
        genai.configure(api_key=st.session_state["api_key"])
    
    # Set Title
    title = st.text_input("Set Title")
    logger.info(f"Title: {title}")
    
    # Display Selected Images
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.image(str(st.session_state["selected_images"][i]), use_column_width=True)
    
    # Set Prompt 
    prompt = GEMINI_PROMPT.format(title)
    logger.info(f"Prompt: {prompt}")

    # Call API
    if st.button("Calculate Score"):
        scores = []
        for i in range(4):
            with cols[i]:
                if st.session_state["model"] == "gemini":
                    img = Image.open(st.session_state["selected_images"][i])
                    score = call_gemini_api(prompt, img)
                elif st.session_state["model"] == "gpt4":
                    img_path = st.session_state["selected_images"][i]
                    score = call_gpt4_api(prompt, img_path, st.session_state["api_key"])
                logger.info(f"Score: {score}")
                st.write(f"Score: {score}")
                scores.append(score)

        # Vote
        st.write("Vote Results")
        cols = st.columns(1)
        argmax_idx = int(np.argmax(scores))
        st.image(str(st.session_state["selected_images"][argmax_idx]), use_column_width=True)
        

if __name__ == "__main__":
    if not st.session_state.get("IsSelected", False):
        logger.debug("Transition to select page")
        select_page()
    elif not st.session_state.get("setting", False):
        logger.debug("Transition to setting page")
        setting_page()
    else:
        logger.debug("Transition to main page")
        main_page()