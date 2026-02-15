from dotenv import load_dotenv
import os
import sys
import requests
import base64
import mss
import datetime, random, time
import json as json_imported
from flask import Flask, render_template
import threading

load_dotenv()

data = {}
lock = threading.Lock()

def encode_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def ask(img):
    image_data = encode_img(img)
    r = requests.post(
        "https://ai.hackclub.com/proxy/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-5-mini",
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
        },
        timeout=60
    )

    if r.status_code != 200:
        raise RuntimeError(r.text)

    payload = r.json()
    content = payload.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise ValueError("empty model output")

    json_imported.loads(content)
    return content

def take_ss():
    now = datetime.datetime.now()
    filename = now.strftime("%H-%M-%S-%d-%m-%Y.png")
    with mss.mss() as sct:
        sct.shot(output=filename)
    return filename

def get_info():
    img = take_ss()
    try:
        return ask(img)
    finally:
        if os.path.exists(img):
            os.remove(img)

lock = threading.Lock()

def update_data(json_text):
    global data
    now = datetime.datetime.now()
    parsed = json_imported.loads(json_text)

    with lock:
        data[now.strftime("%H-%M-%S-%d-%m-%Y")] = {
            "type": parsed["action"]["type"],
            "text": parsed["action"]["text"]
        }

def worker_loop():
    while True:
        try:
            text = get_info()
            if text.strip():
                update_data(text)
        except Exception as e:
            print("Worker error:", repr(e))
        time.sleep(random.randint(5, 12))

app = Flask(__name__)

def loadData():
    global data
    with lock:
        parsed = []
        for t, d in data.items():
            entry = datetime.datetime.strptime(t, "%H-%M-%S-%d-%m-%Y")
            parsed.append({
                "dt": entry,
                "datetime": entry.strftime("%H:%M:%S %d/%m/%Y"),
                "type": d.get("type"),
                "text": d.get("text")
            })

        parsed.sort(key=lambda x: x["dt"])
        return parsed

@app.route("/")
def index():
    data = loadData()
    return render_template("index.html", database=data)

if __name__ == "__main__":
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)