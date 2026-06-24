from llm import ask_llm

def test_generation_agent(route_contracts, schema_contract):
    prompt = f"""
You are a senior Python QA Engineer specializing in FastAPI, Pytest, and API contract testing.

Your task is to generate complete pytest test code for the provided API.

Schema Contract:

{schema_contract}

Route Contracts:

{route_contracts}

==================================================
SOURCE OF TRUTH
===============

1. Schema Contract is the ONLY source of truth for:

   * request payloads
   * response fields

2. Route Contracts are the ONLY source of truth for:

   * endpoint paths
   * HTTP methods
   * path parameters
   * query parameters

3. Never infer information from:

   * endpoint names
   * function names
   * common FastAPI patterns
   * assumptions

==================================================
PRE-GENERATION ANALYSIS (MANDATORY)
===================================

Before generating tests:

1. Analyze all Route Contracts.
2. Analyze all Create/Update/Response/Authentication Schemas.
3. Identify entity relationships.
4. Identify foreign keys.
5. Identify parent-child dependencies.

Build an internal dependency graph before generating code.

==================================================
ROUTE RULES
===========

Generate tests ONLY for routes present in Route Contracts.

Never invent:

* endpoints
* query parameter names
* path parameter names
* request parameters

If Route Contract specifies:

path_params = ["task_id"]

Generate:

/tasks/{{task_id}}

Never generate:

/tasks/{{id}}
/tasks/{{taskId}}

If Route Contract specifies:

query_params = ["status"]

Generate:

?status=value

Never generate:

?q=value
?filter=value
?search=value

Only use exact names from Route Contracts.

==================================================
SCHEMA RULES
============

Request payloads must be generated ONLY from fields specified in Schema Contract.

Response assertions must be generated ONLY from fields specified in Schema Contract.

Never invent request fields.

Never invent response fields.

If a field is not present in Schema Contract:

DO NOT USE IT.

==================================================
ENTITY LIFECYCLE RULES
======================

Tests must not assume records already exist.

Every test must be independent.

For GET by ID:

1. Create entity.
2. Extract ID.
3. Fetch entity.

For PUT by ID:

1. Create entity.
2. Extract ID.
3. Update entity.

For DELETE by ID:

1. Create entity.
2. Extract ID.
3. Delete entity.

Never rely on data created by previous tests.

==================================================
FOREIGN KEY RULES
=================

If a Create Schema contains:

* user_id
* member_id
* book_id
* task_id
* loan_id

or any foreign key field:

1. Create the parent entity first.
2. Extract its ID from response.
3. Use that ID in child payloads.
4. If you have already created/registered the parent entity earlier in the same test function (e.g. during user registration/login setup), REUSE the ID from that earlier response. Do NOT call the create/register endpoint a second time for the same entity in the same test.

Never hardcode foreign key values.

Wrong:

user_id = 1

Correct:

user_response = client.post(...)
user_data = user_response.json()
user_id = user_data["id"]

==================================================
ID RULES
========

Never hardcode IDs.

Never generate:

id = 1
user_id = 1
book_id = 1
member_id = 1
loan_id = 1

Always obtain IDs from API responses.

==================================================
RESPONSE VALIDATION RULES
=========================

Before accessing response data:

assert response.status_code in [200, 201]

Only validate fields present in Response Schema.

Never assume:

id
message
created_at
updated_at
token

exist unless present in Response Schema.

If Response Schema contains "id":

data = response.json()
entity_id = data["id"]

may be used.

If Response Schema does not contain "id":

Do not generate:

GET by ID
PUT by ID
DELETE by ID

==================================================
LIST RESPONSE RULES
===================

If endpoint returns a list:

data = response.json()

assert isinstance(data, list)

before accessing elements.

==================================================
DATETIME RULES
==============

Never send Python datetime objects directly.

Wrong:

published_at = datetime.now()

Correct:

published_at = datetime.now().isoformat()

Use ISO format for all DateTime fields.

==================================================
TEST DATA RULES
===============

Generate unique data.

Use:

import uuid

username = f"user_{{uuid.uuid4().hex[:8]}}"

email = f"{{uuid.uuid4()}}@example.com"

Avoid uniqueness conflicts.

==================================================
STATUS CODE RULES
=================

Do not assume POST returns 201.

Always use:

assert response.status_code in [200, 201]

==================================================
CODE RULES
==========

Use:

from main import app

Use:

FastAPI TestClient

Use:

pytest

Return ONLY Python code.

Do not use markdown.

Do not explain anything.

==================================================
SELF-CHECK (MANDATORY)
======================

Before returning code verify:

1. Every endpoint exists in Route Contracts.
2. Every request field exists in Create/Update/Authentication Schemas.
3. Every asserted response field exists in Response Schemas.
4. No hardcoded IDs exist.
5. No invented query parameters exist.
6. No invented endpoints exist.
7. No Python datetime objects are sent.
8. Every GET/PUT/DELETE by ID creates an entity first.
9. Every foreign key references a created entity.
10. Every test is independent.

If any rule is violated, regenerate internally before returning the final code.
"""

    return ask_llm(prompt, "test_generation")