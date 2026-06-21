from llm import ask_llm

def repair_test_code(
    test_code,
    error_message,
    route_contracts,
    schemas_code
):

    prompt = f"""
You are a senior FastAPI QA engineer.

Current Test Code:

{test_code}

Actual Failure:

{error_message}

Route Contracts:

{route_contracts}

Schemas:

{schemas_code}

Fix ONLY the failing test.

Rules:

1. Preserve working tests.
2. Use Route Contracts as source of truth.
3. Use exact query parameter names.
4. Use exact path parameter names.
5. Use only schema fields.
6. Do not invent routes.
7. Return ONLY Python code.
"""

    fixed_code = ask_llm(prompt)

    return fixed_code