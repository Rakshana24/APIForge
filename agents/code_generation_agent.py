from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def code_generation_agent(blueprint):

    prompt = prompt = f"""
You are a senior FastAPI and SQLAlchemy developer.

Given the following architecture blueprint:

{blueprint}

Generate ONLY the content of models.py.

Rules:

1. Use SQLAlchemy ORM.

2. Roles such as Admin, User, Moderator are NOT separate models.
   Store roles as a field inside the User model.

3. Generate models only for actual entities.

4. Generate proper ForeignKey relationships.

5. Generate proper relationship() mappings.

6. Use:
   completed = Column(Boolean, default=False)

7. Use:
   nullable=False
   for important fields.

8. Import:

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base

9. Return ONLY Python code.

10. Do NOT use markdown.

11. Do NOT explain anything.

12. Do NOT create tables for roles.

13. Every model must contain:
    __tablename__
IMPORTANT:

1. Model class names MUST use PascalCase.

Examples:
User
Book
Task

2. Never generate:

class user
class book
class task

3. SQLAlchemy relationships must reference PascalCase model names.

Examples:

relationship("User")
relationship("Book")
relationship("Task")

4. Return only valid Python code.

14. Use snake_case naming.
IMPORTANT:

If a model contains a field named created_at:

Generate:

created_at = Column(
    DateTime,
    default=datetime.utcnow,
    nullable=False
)

If a model contains a field named updated_at:

Generate:

updated_at = Column(
    DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
    nullable=False
)

Import:

from datetime import datetime
from sqlalchemy import DateTime
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

    code = response.choices[0].message.content

    return code
def database_generation_agent():

    return """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
"""
def schema_generation_agent(blueprint,model_contract):

    prompt = f"""
You are a senior FastAPI developer.

Given this architecture blueprint:

{blueprint}

Model Contract:

{model_contract}

RULES:

1. The Model Contract is the source of truth.
2. Generate schema fields only from Model Contract.
3. Never invent fields.
4. Every Create schema field must exist in the Model Contract.
5. Every Response schema field must exist in the Model Contract.


DateTime database fields must generate:

from datetime import datetime

created_at: datetime
updated_at: datetime
published_at: datetime

Never use:

created_at: str
updated_at: str
published_at: str

Response schemas must use datetime type for DateTime fields.
IMPORTANT:

Generate schemas ONLY for models listed in Available Models.

Never generate schemas for models that are not present in Available Models.
Generate ONLY the content of schemas.py.

If a model contains a non-nullable foreign key:

Example:
user_id = Column(Integer, ForeignKey(...), nullable=False)

Then the corresponding Create schema MUST contain:

user_id: int

Never omit required foreign keys.

Requirements:

1. Use Pydantic.

2. Import:
from pydantic import BaseModel
from typing import Optional

3. For each model generate:

- Create Schema
- Response Schema

Example:

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

4. Do NOT expose password_hash in response schemas.

5. Do NOT expose password in response schemas.

6. Use proper Python class names.

7. Return ONLY Python code.

8. Do NOT use markdown.

9. Do NOT explain anything.
IMPORTANT: RESPONSE SCHEMA GENERATION RULES

1. Generate schemas ONLY from the generated model fields.

2. Never invent fields.

3. Every field in Response schemas must exist in the corresponding SQLAlchemy model.

4. Allowed additional fields:
   - id
   - created_at
   - updated_at

ONLY if they exist in the model.

5. Before generating a Response schema:

ResponseSchemaFields ⊆ ModelFields

must be true.

6. Never generate fields such as:

published_at
status
metadata
last_login
description

unless those fields explicitly exist in the model.
If authentication is enabled:

Generate:

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
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
def route_generation_agent(blueprint,schema_contract):

    prompt = f"""
You are a senior FastAPI backend engineer.

Architecture Blueprint:

{blueprint}

Schema Contract:

{schema_contract}

==================================================
SOURCE OF TRUTH
===============

1. Schema Contract is the ONLY source of truth.

2. Use ONLY:

   * schema names
   * request fields
   * response fields

   present in Schema Contract.

3. Never invent:

   * schema names
   * request fields
   * response fields
   * login fields
   * search fields
   * foreign key fields

4. If a field is not present in Schema Contract:

   DO NOT USE IT.

==================================================
PRE-GENERATION ANALYSIS (MANDATORY)
===================================

Before generating any code:

1. Analyze all models from Architecture Blueprint.

2. Analyze all schemas from Schema Contract.

3. Build a mapping:

   Entity
   ↓
   Create Schema
   ↓
   Response Schema

4. For every route determine:

   * request schema
   * response schema
   * SQLAlchemy model

5. Verify every attribute used in route handlers exists in the corresponding Create Schema.

6. Verify every response field exists in the corresponding Response Schema.

7. If a schema is missing:

   do not invent one.

==================================================
ROUTE GENERATION RULES
======================

Generate CRUD endpoints for all entities.

Include:

* GET all
* GET by ID
* POST
* PUT
* DELETE

Use FastAPI APIRouter.

Use SQLAlchemy ORM.

Use dependency injection.

Return only valid FastAPI code.

==================================================
ROUTE ORDERING RULES
====================

When multiple routes share a common path prefix:

Static routes must be declared before dynamic routes.

Static route example:

/resource/search

Dynamic route example:

/resource/{id}

Always place fixed path routes before parameterized routes.

This prevents FastAPI route matching conflicts.

==================================================
SCHEMA USAGE RULES
==================

Only access attributes present in Create Schema.

Example:

If Create Schema contains:

title
description
completed

Valid:

obj.title
obj.description
obj.completed

Invalid:

obj.created_at
obj.updated_at
obj.user_id

unless those fields exist in schema.

==================================================
SQLALCHEMY RULES
================

Only SQLAlchemy model instances may be used with:

db.add(...)
db.refresh(...)
db.delete(...)

Never add Pydantic schemas to database.

Invalid:

db.add(user)

where user is UserCreate.

Valid:

new_user = User(
username=user.username,
email=user.email
)

db.add(new_user)

==================================================
TIMESTAMP RULES
===============

Never manually assign:

created_at
updated_at

These are managed by model defaults.

==================================================
GET BY ID RULES
===============

Use:

obj = db.query(...).filter(...).first()

If obj is None:

raise HTTPException(
status_code=404,
detail="<Entity> not found"
)

Never return None for endpoints using response_model.

==================================================
AUTHENTICATION RULES
====================

If LoginRequest exists:

Use LoginRequest for login input.

Never use UserCreate for login.

If LoginResponse exists:

Use LoginResponse as response_model.

Return exactly the fields defined in LoginResponse.

==================================================
RESPONSE MODEL RULES
====================

Every endpoint returning data must define response_model.

GET ALL:

response_model=list[ResponseSchema]

GET BY ID:

response_model=ResponseSchema

POST:

response_model=ResponseSchema

PUT:

response_model=ResponseSchema

Never omit response_model.

==================================================
SELF-CHECK (MANDATORY)
======================

Before returning code verify:

1. Every schema used exists in Schema Contract.
2. Every attribute accessed exists in Create Schema.
3. Every response_model exists in Schema Contract.
4. No invented fields exist.
5. No invented schemas exist.
6. No Pydantic model is passed to db.add().
7. No manual created_at assignment exists.
8. No manual updated_at assignment exists.
9. Static routes appear before dynamic routes.
10. Every data-returning endpoint has response_model.

If any check fails:

Regenerate internally before returning code.

Return ONLY Python code.
No markdown.
No explanations.

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
def main_generation_agent():

    return """
from fastapi import FastAPI

import models

from database import Base, engine
from routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="APIForge Generated Backend"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "APIForge Generated Backend"
    }
"""