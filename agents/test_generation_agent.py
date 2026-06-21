from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def test_generation_agent(blueprint, schemas_code, routes_code,route_contracts):

    prompt = f"""
You are a senior Python QA engineer.

Given the following architecture blueprint:

{blueprint}

Generated Schemas:

{schemas_code}

Generated Routes:

{routes_code}


Route Contracts:

{route_contracts}

ROUTE CONTRACTS ARE THE SOURCE OF TRUTH.

Before generating tests:

1. Analyze all Route Contracts.

2. Use only:
   - endpoint paths
   - HTTP methods
   - path parameters
   - query parameters

   defined in Route Contracts.

3. Never invent:
   - endpoints
   - query parameter names
   - path parameter names
   - request parameter names

4. For every request:

   Path parameters must match the route contract.

   Query parameters must match the route contract.

5. If Route Contract contains:

   path_params = ["task_id"]

   Generate:

   /tasks/{{task_id}}

   Never generate:

   /tasks/{{id}}
   /tasks/{{taskId}}

6. If Route Contract contains:

   query_params = ["status"]

   Generate:

   ?status=value

   Never generate:

   ?state=value
   ?filter=value
   ?q=value

7. Do not infer parameter names from:
   - endpoint names
   - function names
   - common API patterns

8. Route Contracts are the only source of truth for API structure.

9. If a parameter is not present in Route Contracts:

   do not use it.

10. Generate tests strictly from Route Contracts.

Generate pytest test code.

GENERAL RULES

1. Use pytest.
2. Use FastAPI TestClient.
3. Generate tests for all available GET, POST, PUT, and DELETE endpoints.
4. Return ONLY Python code.
5. Do not use markdown.
6. Do not explain anything.
7. Import app using:

from main import app

8. Never use:

from generated_project.main import app
---
ROUTE RULES

1. Generate tests ONLY for routes present in routes.py.
2. Never invent endpoints.
3. Do not generate tests for routes that do not exist.
4. Never generate routes such as:

/reports
/analytics
/stats
/search

unless they explicitly exist in routes.py.
---
SCHEMA RULES

1. Analyze all Create schemas.
2. Analyze all Response schemas.
3. Generate request payloads ONLY from Create schemas.
4. Generate response assertions ONLY from Response schemas.
5. Never invent request fields.
6. Never invent response fields.
7. The provided schemas are the only source of truth.
8. Do not infer fields from endpoint names.
9. Do not infer fields from common FastAPI patterns.
---
ENTITY LIFECYCLE RULES

1. Tests must not assume database records already exist.
2. Create entities before retrieving, updating, or deleting them.
3. Do not hardcode IDs.
4. Use IDs returned from create responses.
5. Never create the same entity twice merely to obtain an ID.
6. Reuse the original create response.
7. Every test must be independent.
8. Tests must not depend on data created by previous tests.
---
RESPONSE VALIDATION RULES

1. Before accessing response fields:

assert response.status_code in [200, 201]

2. If a field exists in the Response schema, it may be validated.

3. If a field does not exist in the Response schema, never reference it.

4. If "id" exists in the Response schema:

data = response.json()
entity_id = data["id"]

may be used.

5. If "id" does not exist in the Response schema:

do not generate GET-by-id, PUT-by-id, or DELETE-by-id tests.

6. If an endpoint returns a list:

verify the response is a list before accessing elements.

7. Never assume any endpoint returns:

id
message
created_at
updated_at

unless those fields exist in the corresponding Response schema.
---
STATUS CODE RULES

1. Do not assume POST returns 201.
2. Accept:

200
or
201

Example:

assert response.status_code in [200, 201]
---
DATETIME RULES

1. Never send Python datetime objects directly in JSON.

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
2. Use datetime.now().isoformat() for all DateTime fields.

---

TEST DATA RULES

1. Generate unique test data.

Example:

import uuid

username = f"user_{{uuid.uuid4().hex[:8]}}"
email = f"{{uuid.uuid4()}}@example.com"

2. Never reuse fixed values that may cause uniqueness conflicts.

---

CRITICAL RULE

Before generating tests:

1. Analyze all routes.
2. Analyze all Create schemas.
3. Analyze all Response schemas.
4. Build tests strictly from those routes and schemas.

Routes are the source of truth for available endpoints.

Create schemas are the source of truth for request payloads.

Response schemas are the source of truth for response assertions.

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