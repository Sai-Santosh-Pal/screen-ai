from openrouter import OpenRouter

client = OpenRouter(
    api_key="sk-hc-v1-6b1b1b47cb1f44c48b6c7372082df62da2259fec3f0448c2a8bfc4f4338e2576", 
    server_url="https://ai.hackclub.com/proxy/v1"
)

asked = str(input("Prompt: "))

response = client.chat.send(
    model="openai/gpt-5.1",
    messages=[
        {"role":"user","content":f"{asked}"}
    ],
    stream=False
)

print(response.choices[0].message.content)