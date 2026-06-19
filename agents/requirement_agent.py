from llm import ask_llm
import re
import json
def requirement_agent(user_requirement):

    prompt = f"""
You are a backend requirement analyst.

Analyze the following software requirement.

Requirement:
{user_requirement}

Return ONLY valid JSON.

Format:

{{
    "project_name": "",
    "description": "",
    "entities": [],
    "authentication": false,
    "roles": [],
    "features": []
}}

Rules:

1. Entity names must be singular.
   Correct:
   User
   Task
   Book

   Wrong:
   Users
   Tasks
   Books

2. Features must contain the main functionality.

3. authentication must be true or false.

4. roles must contain user roles.

5. Return JSON only.

Roles are NOT entities.

Examples:
Admin
User
Librarian
Moderator

must be stored in the User.role field.

Infrastructure concepts are NOT entities.

Examples:
Database
API
Backend
Frontend
Server
Authentication

must never become models.


IMPORTANT:

Roles are NOT entities.

Examples:
Admin
User
Librarian
Moderator

must be added to the "roles" array.

Do NOT add them to the "entities" array.

Infrastructure concepts are NOT entities.

Examples:
Database
API
Backend
Frontend
Server
Authentication
Authorization

must never appear in the "entities" array.
IMPORTANT:

Return ONLY raw JSON.

Do not write:

"Here is the JSON"

"Based on the requirement"

or any explanation.

The first character of the response must be {{

The last character of the response must be }}
Only business domain objects should become entities.

Examples:

Library:
Book
Member
Loan

Hospital:
Patient
Doctor
Appointment

E-Commerce:
Product
Order
Cart
"""
    result = ask_llm(prompt)
    
    
    print("\nRAW MODEL OUTPUT   :")
    print(result)
    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()
    match = re.search(
        r"\{.*\}",
        result,
        re.DOTALL
    )
    if not result:
        raise Exception("Empty response from model")
    if not match:
        raise Exception(f"No JSON found in response:\n{result}")
    result = match.group(0)
    print("\nEXTRACTED JSON:")
    print(result)
    return json.loads(result)