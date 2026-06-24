from llm import ask_llm

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

    return ask_llm(prompt, "repair")