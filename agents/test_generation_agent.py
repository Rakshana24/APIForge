from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def test_generation_agent(blueprint, schemas_code):

    prompt = f"""
You are a senior Python QA engineer.

Given the following architecture blueprint:

{blueprint}

Generated Schemas:

{schemas_code}

Generate pytest test code.

Requirements:

1. Use pytest.

2. Use FastAPI TestClient.

3. Generate tests for GET endpoints.

4. Generate tests for POST endpoints.

5. Generate tests for PUT endpoints if present.

6. Generate tests for DELETE endpoints if present.

7. Use the provided schemas when generating test payloads.

8. Only use fields that exist in the schemas.

9. Do not invent fields.

10. Return ONLY Python code.

11. Do not use markdown.

12. Do not explain anything.

IMPORTANT:

1. Tests must not assume database records already exist.

2. If a test needs an entity:
   - create it first
   - then test retrieval
   - then test update
   - then test deletion

3. Do not hardcode IDs.

4. Use data created during the test.

5. Generate realistic pytest tests.

6. The application entrypoint is:

   main

7. Import using:

   from main import app

8. Never use:

   from generated_project.main import app

9. Use only fields present in Create schemas.

10. Never omit required fields.

11. Generate unique test data.

Example:

import uuid

username = f"user_{{uuid.uuid4().hex[:8]}}"
email = f"{{uuid.uuid4()}}@example.com"

12. Tests must not depend on data created by previous tests.

13. Every test must be independent.

IMPORTANT:

1. Never assume login returns an id.

2. Generate tests according to LoginResponse schema.

3. Before accessing response fields:

   assert response.status_code == expected_status

4. If login fails:

   do not continue using response.json()["id"]

5. Only use fields that exist in the response schema.
For login tests:

Use LoginRequest fields only.

Do not assume login returns id.

Do not use login response to obtain user_id.

IMPORTANT:

1. Use response schemas when validating API responses.

2. If a response schema does not contain an "id" field:

   do not access response.json()["id"]

3. Before using any response field:

   assert "<field>" in response.json()

4. Never assume login returns:

   id
   email
   role
   username

5. Only use fields explicitly defined in the corresponding response schema.

6. If an endpoint returns a list:

   verify it is a list before accessing elements.

7. If a required field is unavailable:

   generate the test using only available response fields.

IMPORTANT:

1. Tests must be generated according to the actual schemas provided.

2. Response assertions must use fields present in Response schemas only.

3. Request payloads must use fields present in Create schemas only.

4. Never invent:
   UserUpdate
   TaskUpdate
   BookUpdate

unless they are present in the provided schemas.

5. Never invent:
   id
   created_at
   updated_at

unless they exist in the corresponding response schema.

6. Generate robust tests that fail gracefully when API responses differ from expectations.

IMPORTANT:

If a schema contains DateTime fields:

Never send Python datetime objects directly in JSON.

INVALID:

published_at = datetime.now()

json={{
    "published_at": published_at
}}

VALID:

published_at = datetime.now().isoformat()

json={{
    "published_at": published_at
}}


Do not assume POST returns 201.

Accept either:

200
or
201

Example:

assert response.status_code in [200, 201]


IMPORTANT: ENTITY CREATION RULES

1. Never assume a response contains:

   id
   message
   created_at
   updated_at

2. Before using any response field:

   verify that field exists in the corresponding Response schema.

3. Only access:

   response.json()["field"]

   if that field is explicitly present in the Response schema.

4. If the Response schema does not contain id:

   never generate:

   response.json()["id"]

   assert "id" in response.json()

5. If the Response schema does not contain message:

   never generate:

   response.json()["message"]

   assert "message" in response.json()

6. For create endpoints:

   validate only fields that exist in the Response schema.

7. If id exists in the Response schema:

   response = client.post(...)

   assert response.status_code in [200, 201]

   data = response.json()

   entity_id = data["id"]

   reuse entity_id for GET, PUT and DELETE tests.

8. If id does not exist in the Response schema:

   do not generate GET-by-id, PUT-by-id or DELETE-by-id tests.

9. Never create the same entity twice merely to obtain an id.

10. Never invent response fields.

11. Never invent request fields.

12. Use only fields defined in the provided schemas.

13. Registration endpoints must be validated according to their actual response schema.

14. Never assume registration returns:

{{
"message": "..."
}}

15. Login endpoints must be validated according to LoginResponse only.

16. Never assume login returns:

id
username
email
role

17. If a response schema contains only:

{{
"token": str
}}
then validate only token.

18. If a response schema contains only:

{{
"success": bool
}}

then validate only success.

19. Schema-driven assertions only.

If a field exists in the Response schema:
it may be accessed.

If a field does not exist in the Response schema:
never reference it.

Examples:

VALID:

assert "id" in response.json()
user_id = response.json()["id"]

only when id exists in the Response schema.

INVALID:

assert "message" in response.json()
response.json()["message"]

when message is not defined in the Response schema.

20. Generate schema-driven assertions only.


21. Before generating tests:

Analyze all Create schemas.
Analyze all Response schemas.

Build tests strictly from those schemas.

Do not infer fields from endpoint names.

Do not infer fields from common FastAPI patterns.

The schemas are the only source of truth.



CRITICAL:

Never generate:

assert "message" in response.json()

response.json()["message"]

unless the corresponding Response schema explicitly contains a field named message.

Never generate:

assert "id" in response.json()

response.json()["id"]

unless the corresponding Response schema explicitly contains a field named id.

The provided schemas are the only source of truth.

If a field does not exist in the schema, do not validate it.

Use datetime.now().isoformat() for DateTime fields.

Do NOT use raw datetime objects in JSON payloads.

IMPORTANT:

Never call the same POST endpoint twice with identical payloads.

BAD:

client.post("/users", json=user_data)
user_id = client.post("/users", json=user_data).json()["id"]

GOOD:

response = client.post("/users", json=user_data)
user_id = response.json()["id"]

Reuse the original response.
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