from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def repair_agent(code, error_message):

    prompt = f"""
You are a senior FastAPI developer.

The following code contains errors.

Error:

{error_message}

Code:

{code}

Fix the code.

Rules:

1. Return ONLY corrected Python code.
2. Do not use markdown.
3. Do not explain anything.
4. Preserve functionality.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content