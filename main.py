from dotenv import load_dotenv
import os
import requests
import base64
import mss
import datetime

load_dotenv()
api_key = os.getenv("API_KEY")

def encode_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def ask(img, prompt):
    image_data = encode_img(img)
    response = requests.post(
        "https://ai.hackclub.com/proxy/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-5.1", # or google/gemini-2.5-flash
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{prompt}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        }
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]

def take_ss():
    path = datetime.datetime.now()
    with mss.mss() as sct:
        sct.shot(output=path.strftime("%H-%M-%S-%d-%m-%Y"))
    return path.strftime("%H-%M-%S-%d-%m-%Y")

print(take_ss())

def get_next_task(goal):
    current_pos = take_ss()
    return ask(current_pos, goal)