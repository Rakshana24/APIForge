import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Initialize Groq client
groq_client = None
groq_api_key = os.environ.get("GROQ_API_KEY")
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)

MODEL_CONFIG = {
    "clarification": {
        "provider": "groq",
        "model": "qwen/qwen3-32b"
    },
    "requirement": {
        "provider": "groq",
        "model": "qwen/qwen3-32b"
    },
    "architecture": {
        "provider": "groq",
        "model": "qwen/qwen3-32b"
    },
    "repair": {
        "provider": "groq",
        "model": "qwen/qwen3-32b"
    },
    "model_generation": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b"
    },
    "schema_generation": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b"
    },
    "route_generation": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b"
    },
    "test_generation": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b"
    }
}

def strip_thinking(text):
    if not text:
        return text
    # Remove <think>...</think> tags and their contents
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()

def ask_llm(prompt, agent):
    config = MODEL_CONFIG[agent]
    provider = config["provider"]
    model = config["model"]

    if provider == "groq":
        if not groq_client:
            raise ValueError("GROQ_API_KEY is not configured but a Groq model was requested.")
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=4096
        )
        return strip_thinking(response.choices[0].message.content)

    # Fallback to Ollama
    raise ValueError("Ollama is disabled. Only Groq provider is supported.")