from dotenv import load_dotenv
import os
import requests
import base64
import mss
import datetime, random, time
import json as json_imported
from flask import Flask, render_template
import threading

load_dotenv()
api_key = os.getenv("API_KEY")

def encode_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def ask(img):
    image_data = encode_img(img)
    response = requests.post(
        "https://ai.hackclub.com/proxy/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen/qwen3-vl-235b-a22b-instruct", #"openai/gpt-5.1", # or google/gemini-2.5-flash
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """
                        SYSTEM: YOU ARE A SCREEN CONENT ANALYZER. YOU SEE EXACTLY ONE SCREENSHOT AT A TIME. YOU MUST OUTPUT EXACTLY ONE ACTION IN STRICT JSON. YOU MUST NEVER ADD UP THINGS ON YOUR OWN AND FOCUS ONLY ON THE SCREENSHOT'S OVERVIEW

                        USER: HERE IS THE ATTACHED SCREENSHOT ANALYZE THE SCREENSHOT ONLY AND ONLY, OUTPUT A SINGLE ACTION IN JSON WITH FOLLOWING FORMATING ONLY:
                        {
                            "action": {
                                "type": "study" | "coding" | "learning" | "doomscrolling" | "other",
                                "text": "<string, remarks in detail>"
                            }
                        }
                        CONSTRAINTS:
                        0. The text should be not state - The screenshot - instead - You were...
                        1. OUTPUT MUST BE VALID JSON AND PARSEABLE
                        2. ONLY INCLUDE ONE ACTION
                        3. DONT ADD COMMENTARY OR ANY EXTRAS
                        """},
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
        sct.shot(output=path.strftime("%H-%M-%S-%d-%m-%Y.png"))
    return path.strftime("%H-%M-%S-%d-%m-%Y.png")


def get_info():
    current_pos = take_ss()
    return ask(current_pos)

def update_data(json):
    time = datetime.datetime.now()
    json = json_imported.loads(json)
    # data[] = {"type": json["action"]["type"], "text": json["action"]["text"]}
    with open('data.json', "r", encoding="utf-8") as f:
        data = json_imported.load(f)
    data[time.strftime("%H-%M-%S-%d-%m-%Y")] = {"type": json["action"]["type"], "text": json["action"]["text"]}
    print(data)

    with open('data.json', "w", encoding="utf-8") as f:
        json_imported.dump(data, f, indent=2)

def run():
    while True:
        time.sleep(random.randint(0, 5))
        update_data(get_info())

# run()
# dummy = {
#     "action": {
#         "type": "coding",
#         "text": "You were actively editing Python code in a code editor, implementing functions for API requests and screenshot handling, with the terminal indicating the script is being executed, confirming active coding work."
#     }
# }
# update_data(dummy)

# rendering

app = Flask(__name__)

def loadData():
    with open('data.json', "r", encoding="utf-8") as f:
        data = json_imported.load(f)

    parsed=[]
    # print(data.items())
    for t, d in data.items():
        entryTime = datetime.datetime.strptime(t, "%H-%M-%S-%d-%m-%Y")
        parsed.append({"datetime": entryTime, "type": d.get("type"), "text": d.get("text")})
    print(parsed)

    parsed.sort(key=lambda x: x["datetime"])
    return parsed

@app.route("/")
def index():
    data = loadData()
    return render_template("index.html", database=data)

def execute():
    while True:
        run()

if __name__ == "__main__":
    t = threading.Thread(target=execute, daemon=True)
    t.start()
    app.run(debug=False)