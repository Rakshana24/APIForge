from llm import ask_llm

def code_generation_agent(model_contract):
    prompt = f"""
You are a senior FastAPI and SQLAlchemy developer.

Given the following Model Contract:

{model_contract}

Generate ONLY the content of models.py.

Rules:

1. Use SQLAlchemy ORM.

2. Roles such as Admin, User, Moderator are NOT separate models.
   Store roles as a field inside the User model.

3. Generate models only for actual entities.

4. Generate proper ForeignKey relationships.

5. Generate proper relationship() mappings.

6. Use the field names specified in the Model Contract for Boolean/completed status fields (e.g. is_completed = Column(Boolean, default=False)).

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

    code = ask_llm(prompt, "model_generation")
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

def schema_generation_agent(schema_contract):
    prompt = f"""
You are a senior FastAPI developer.

Given this Schema Contract:

{schema_contract}

RULES:

1. Every field listed in the Schema Contract for a schema class MUST be included in the generated Pydantic model class. For example, if "user_id" is in "TaskCreate", you MUST generate "user_id: int" (or other appropriate type) in TaskCreate. Never omit foreign keys (like user_id, owner_id, etc.) if they are defined in the schema.
2. The Schema Contract is the source of truth for all schema class names and their fields.
3. Generate schemas ONLY for the schemas listed in the Schema Contract.
4. Every schema class you generate must contain EXACTLY the fields specified in the Schema Contract.
4. Never invent fields or schemas.

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
Generate ONLY the content of schemas.py.

Requirements:

1. Use Pydantic.

2. Import:
from pydantic import BaseModel
from typing import Optional

3. For each schema listed in Schema Contract generate:
- BaseModel schema

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

1. Every field in Response schemas must exist in the contract.
If authentication is enabled, generate:

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
"""

    return ask_llm(prompt, "schema_generation")

def route_generation_agent(route_contracts, schema_contract, model_contract):
    prompt = f"""
You are a senior FastAPI backend engineer.

Route Contract:

{route_contracts}

Schema Contract:

{schema_contract}

Model Contract:

{model_contract}

==================================================
SOURCE OF TRUTH
===============

1. Schema Contract is the source of truth for all schema names and fields.

2. Route Contract is the source of truth for route function names, methods, paths, and parameters.
   Use ONLY:
   * function names
   * HTTP methods
   * paths
   * path parameters
   * query parameters
   * request_schema
   * response_schema
   present in Route Contract.

3. Never invent function names or endpoints. If the Route Contract defines "create_book" for "POST /books", you must use exactly `def create_book(...)` and `@router.post("/books")`.

==================================================
ROUTE ARCHITECTURE ENFORCEMENT (CRITICAL)
=========================================

Generated route files must contain ONLY:
1. imports
2. router = APIRouter()
3. CRUD handlers

FORBIDDEN inside routes.py:
- SQLAlchemy model definitions (e.g. class User(Base))
- Pydantic schema definitions (e.g. class UserCreate(BaseModel))
- Database initialization (e.g. Base.metadata.create_all)
- FastAPI app creation (e.g. app = FastAPI())

Routes must consume models.py and schemas.py by importing them. You MUST use absolute imports (e.g., `from models import User`, `from schemas import UserCreate`, `from database import get_db`). Relative imports (e.g., `from .models import ...`) are strictly FORBIDDEN and will cause import errors.

==================================================
ROUTE GENERATION RULES
======================

Generate CRUD endpoints for all entities.

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

/resource/{{id}}

Always place fixed path routes before parameterized routes.

This prevents FastAPI route matching conflicts.

==================================================
SCHEMA USAGE RULES
==================

Only access attributes present in Create/Update Schema.

==================================================
SQLALCHEMY RULES
================
Only SQLAlchemy model instances may be used with:

db.add(...)
db.refresh(...)
db.delete(...)

Never add Pydantic schemas to database.

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

You MUST return a dictionary or Pydantic object containing EXACTLY the fields defined in LoginResponse.
For example, if LoginResponse only contains the "message" field, your login function MUST return:
{{"message": "Login successful"}}
Do NOT return "access_token" or "token_type" if they are not in LoginResponse.

==================================================
RESPONSE MODEL RULES
====================

Every endpoint returning data must define response_model.

==================================================
SELF-CHECK (MANDATORY)
======================

Before returning code verify:

1. Every endpoint exists in Route Contracts.
2. Every request field exists in Create/Update Schemas.
3. Every asserted response field exists in Response Schemas.
4. No hardcoded IDs exist.
5. No invented query parameters exist.
6. No invented endpoints exist.
7. No Python datetime objects are sent.

Return ONLY Python code.
No markdown.
No explanations.
"""

    return ask_llm(prompt, "route_generation")

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