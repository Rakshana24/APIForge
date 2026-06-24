from llm import ask_llm
import json


def architecture_agent(specification):

    prompt = f"""
You are a senior FastAPI backend architect.

Given the following software specification:

{json.dumps(specification, indent=2)}

Design the backend architecture.

Return ONLY valid JSON.

JSON Format:

{{
    "models": {{
        "ModelName": {{
            "fields": {{
                "field_name": "field_type"
            }}
        }}
    }},
    "relationships": [
        {{
            "model": "ModelName",
            "related_model": "RelatedModelName",
            "foreign_key": "field_name",
            "relationship_type": "foreign_key"
        }}
    ],
    "routes": [],
    "folder_structure": []
}}

Rules:

1. Generate database models with field types.

2. Supported field types:
   - Integer
   - String
   - Boolean
   - DateTime

3. Roles such as Admin, User, Moderator are NOT separate models.

4. Roles must be stored as a field:
   role: String

5. Never create:
   Admin model
   UserRole model
   Role model

6. Use FastAPI route syntax:
   /tasks/{{id}}

   Never:
   /tasks/:id

7. Include relationships.

8. Include authentication routes if authentication=true.

9. Use singular model names:
   User
   Task
   Book

10. Use snake_case field names.

11. Folder structure MUST be:

[
    "main.py",
    "database.py",
    "models.py",
    "schemas.py",
    "routes/",
    "tests/",
    "README.md",
    "requirements.txt"
]

12. Route format:

{{
    "method": "GET",
    "path": "/tasks/{{id}}",
    "description": "Get task by ID"
}}

13. Return JSON only.

14. Do not include explanations.


IMPORTANT:

The output MUST be valid JSON parsable by Python json.loads().

Use:

true
false
null

Never use:

True
False
None

Do not add trailing commas.

Do not add comments.

Do not add markdown.

Return JSON only.   
"""

    result = ask_llm(prompt, "architecture")

    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    if not result:
        raise Exception("Empty response from model")

    try:
        return json.loads(result)
    except Exception:
        print("MODEL OUTPUT:")
        print(result)
        raise