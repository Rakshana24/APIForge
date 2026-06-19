from ollama import chat

response = chat(
    model="qwen2.5-coder:7b",
    messages=[
        {
            "role": "user",
            "content": "Generate a FastAPI CRUD API for a Todo application"
        }
    ]
)

print(response.message.content)