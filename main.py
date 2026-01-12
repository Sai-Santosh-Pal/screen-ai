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
                        {"type": "text", "text": """
                        SYSTEM: YOU ARE A SCREEN CONTROL REFLEX AGENT. YOU SEE EXACTLY ONE SCREENSHOT AT A TIME. YOU MUST OUTPUT EXACTLY ONE ACTION IN STRICT JSON. YOU MUST NEVER PLAN AHEAD, DESCRIBE, OR INCLUDE MULTIPLE STEPS TO GET TO THE GOAL, OR DESCRIBE, OR INCLUDE MULTIPLE STEPS. COORDINATES HAVE TO BE PIXEL PERFECT SO MAKE SURE YOU CALCULATE PROPERLY (IN PIXELS) ORIGIN AT TOP-LEFT, ALSO TAKE CARE OF THE SCREENSHOT'S RESOLUTION. IF NO ACTION IS REQUIRED, SET "done": true. I REPEAT DO NOT AT ALL INCLUDE ANY EXPLAINATIONS OR TEXT OUTSIDE THE JSON.

                        USER: HERE IS THE ATTACHED SCREENSHOT AND TASK GOAL = """ + prompt + """. ANALYZE THE SCREENSHOT ONLY AND ONLY, OUTPUT A SINGLE ACTION IN JSON WITH FOLLOWING FORMATING ONLY:
                        {
                            "action": {
                                "type": "click" | "move" | "type" | "scroll" | "wait" | "noop",
                                "x": <integer, pixel value coordinate, optional for type/scroll/wait/noop>,
                                "y": <integer, pixel value coordinate, optional for type/scroll/wait/noop>,
                                "button": "left" | "right" | null,
                                "text": "<string, only for type action>",
                                "duration": <integer, ms, optional for wait>
                            },
                            "done": <true|false>,
                            "remarks": "<string, only if necessary>"
                        }
                        CONSTRAINTS:
                        1. OUTPUT MUST BE VALID JSON AND PARSEABLE
                        2. ONLY INCLUDE ONE ACTION PER OUTPUT JSON
                        3. DONT ADD COMMENTARY OR ANY EXTRAS
                        4. IF NO ACTION, IS POSSIBLE, RETURN - {"action":{"type":"noop"},"done":<true|false>, "remarks": "<string>"}
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


def get_next_task(goal):
    print(goal)
    current_pos = take_ss()
    return ask(current_pos, goal)

print(get_next_task("exact coordinates of where should i click to see the extensions in this screenshot"))