import json
import base64
from typing import List

def base64encode_from_bytesimg(img: bytes) -> str:
    return base64.b64encode(img).decode('utf-8')

def load_config(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        return json.load(f)

def save_config(json_path: str, config: dict):
    with open(json_path, 'w') as f:
        json.dump(config, f, indent=4)

def found_kvp(key: str, value: str, target_dict: List[dict]) -> bool:
    found_dict = next((d for d in target_dict if d.get(key) == value), None)
    return found_dict
    