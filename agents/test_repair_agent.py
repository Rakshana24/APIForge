from llm import ask_llm
import re

def apply_localized_repair(code, llm_response):
    target_match = re.search(r"TARGET:\s*```python\n(.*?)\n```", llm_response, re.DOTALL)
    replacement_match = re.search(r"REPLACEMENT:\s*```python\n(.*?)\n```", llm_response, re.DOTALL)
    
    if target_match and replacement_match:
        target = target_match.group(1)
        replacement = replacement_match.group(1)
        
        if target in code:
            return code.replace(target, replacement)
        elif target.strip() in code:
            return code.replace(target.strip(), replacement.strip())
            
    code_match = re.findall(r"```python\n(.*?)\n```", llm_response, re.DOTALL)
    if code_match:
        return code_match[0].strip()
        
    clean_resp = llm_response.replace("```python", "").replace("```", "").strip()
    if len(clean_resp.splitlines()) > 5:
        return clean_resp
        
    return code

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

Identify the specific failing region in the test code and repair only that region. Do NOT regenerate the entire file.

Your response must be formatted EXACTLY as follows:

TARGET:
```python
<exact lines from the original test code to replace>
```

REPLACEMENT:
```python
<repaired lines to replace the target block>
```

Rules:
1. The TARGET block must match a section in the original test code exactly, including leading spaces.
2. The REPLACEMENT block must fix the identified error.
3. Keep the TARGET block as small and localized as possible (e.g. just the single failing test or test function).
4. Return ONLY the TARGET and REPLACEMENT blocks. Do NOT output any other text, explanations, or markdown.
"""

    fixed_code = ask_llm(prompt, "repair")

    return apply_localized_repair(test_code, fixed_code)