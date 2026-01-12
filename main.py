# from openrouter import OpenRouter
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# client = OpenRouter(
#     api_key=api_key, 
#     server_url="https://ai.hackclub.com/proxy/v1"
# )

prompt = str(input("Prompt: "))

# response = client.chat.send(
#     model="openai/gpt-5.1",
#     messages=[
#         {"role":"user","content":f"{asked}"}
#     ],
#     stream=False
# )

# print(response.choices[0].message.content)

import requests
import base64

def encode_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img=input("image: ")
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
print(result["choices"][0]["message"]["content"])