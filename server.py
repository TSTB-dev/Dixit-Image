import os
from flask import Flask, request, jsonify
import logging
import base64
from logging import config

import numpy as np

from PIL import Image

from dotenv import load_dotenv
from openai import Client
import requests


from utils import base64encode_from_bytesimg, load_config, save_config, \
    found_kvp

load_dotenv()
client = Client()
app = Flask(__name__)

GENERATION_CONFIG_PATH = 'config/generation_config.json'
SAVE_DIR = "./data/images"
DATA_CONFIG_PATH = "./data/generated_images.json"

IMAGE_GENERATION_PROMPT = """
Generate an image that matches the following title.
Create visual representations that often blend unrealistic and contradictory elements, drawing inspiration primarily from Japanese animation and watercolor styles.
The generation guideline is here.
- Avoid including any copyrighted or real-world recognizable material.
- Produce images encompassing a background, maintaining a portrait orientation.
- Refrain from incorporating text into the images.
- Use a variety of styles, including beautiful imagery, picture book-style 
- there are no text string image
- If given prompt violates copyright, generate inspired characters for this contents.
The overall style should be Japanese anime style, Japanese watercolor style, or Japanese two-dimensional illustration style.

Generate an image which is inspired from the following title.
Title: {}
"""

PREDICT_SCORE_PROMPT = """
以下のタイトルとこの画像の関連度のスコアを0~1の間で予測してください．出力は小数点第2位まで表示し，数値のみを出力してください．Ex. 0.75
タイトル: {}

出力:
"""

config.fileConfig('config/logging_config.ini')
logger = logging.getLogger(__name__)

def call_gpt4_api(prompt: str, img_base64: str, api_key: str, model_name: str = "gpt-4-vision-preview") -> float:
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
                    "url": f"data:image/jpeg;base64,{img_base64}"
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
        raise ValueError(f"Response: {score} is not float.")  
    return score


@app.route('/generate', methods=['POST'])
def generate_img():
    
    logger.info(f"Request: {request.json}")
    title = request.json.get('title')
    
    generation_config = load_config(GENERATION_CONFIG_PATH)
    prompt = IMAGE_GENERATION_PROMPT.format(title)
    generation_config["prompt"] = prompt
    
    logging.info(f'Generation config: {generation_config}')
    logging.info('Generating image...')
    response = client.images.generate(**generation_config)
    logging.info('Image generated!')
    
    logging.info('Encoding image to base64...')
    img_url = response.data[0].url
    img_bytes = requests.get(img_url).content
    img_base64 = base64encode_from_bytesimg(img_bytes)
    logging.info('Image encoded!')
    
    # save images to local
    data_config = load_config(DATA_CONFIG_PATH)
    img_id = "{:06d}".format(len(data_config["images"]) + 1)
    
    img_path = os.path.join(SAVE_DIR, f"{img_id}.jpg")
    with open(img_path, 'wb') as f:
        f.write(img_bytes)
        
    data_config["images"].append(
        {"id": img_id, "path": img_path, "title": title}
    )
    save_config(DATA_CONFIG_PATH, data_config)
    
    return jsonify({'Image': img_base64, 'ImageId': img_id})

@app.route('/get_image', methods=['POST'])
def get_img():
    logger.info(f"Request: {request.json}")
    img_id = request.json.get('ImageId')
    logging.info(f'Image ID: {img_id}')
    
    logging.info('Loading image...')
    data_config = load_config(DATA_CONFIG_PATH)
    found_dict = found_kvp("id", img_id, data_config["images"])
    if found_dict is None:
        raise ValueError(f"Image ID: {img_id} is not found.")
    
    img_path = found_dict["path"]
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    img_base64 = base64encode_from_bytesimg(img_bytes)
    logging.info('Image loaded!')
    
    return jsonify({'Image': img_base64})
    

@app.route('/vote', methods=['POST'])
def vote_img():
    
    logger.info(f"Request: {request.json}")
    
    img_data = request.json.get('images')
    title = request.json.get('title')
    openai_api_key = os.environ["OPENAI_API_KEY"]
    
    prompt = PREDICT_SCORE_PROMPT.format(title)
    logger.info(f'Prompt: {prompt}')
    
    logger.info(f'Calling GPT-4 API...')
    scores = []
    for img in img_data:
        score = call_gpt4_api(prompt, img, openai_api_key)
        scores.append(score)
    
    vote_id = int(np.argmax(scores))
    logger.info(f'Vote ID: {vote_id}')
    logger.info('Vote completed!')

    return jsonify({'VoteId': vote_id})


if __name__ == "__main__":
    app.run(port=5000)