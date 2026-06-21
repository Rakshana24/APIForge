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
def schema_generation_agent(blueprint,model_names):

    prompt = f"""
You are a senior FastAPI developer.

Given this architecture blueprint:

{blueprint}

Available Models:

{model_names}


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
def route_generation_agent(blueprint,schema_names,schemas_code,model_names):

    prompt = f"""
You are a senior FastAPI developer.

Given the following architecture blueprint:

{blueprint}
Available schemas:

{schema_names}

Generated Schemas:

{schemas_code}

Generate ONLY the content of routes.py.


Available Models:

{model_names}

IMPORTANT:

Import ONLY models from Available Models.

Never import models that are not present in Available Models.

If LoginRequest exists:

Use LoginRequest for /login endpoint.

Never use UserCreate for login.

Requirements:

1. Use FastAPI APIRouter.

2. Import:
from fastapi import APIRouter

3. Generate CRUD endpoints.

4. Include:
   - GET all
   - GET by id
   - POST
   - PUT
   - DELETE

5. Generate routes for all entities.

6. Use FastAPI syntax.

7. Return ONLY Python code.

8. Do not use markdown.

9. Do not explain anything.

Never manually assign:

created_at
updated_at

when creating SQLAlchemy objects.

These fields are automatically handled by model defaults.

Wrong:

Task(
    title=...,
    created_at=datetime.now()
)

Correct:

Task(
    title=...
)
IMPORTANT:

1. NEVER import app from main.py
2. NEVER use:
   from main import app
3. Use APIRouter only.
4. Route files must be independent.
5. main.py will import the router.
IMPORTANT:

1. Use ONLY schema names provided in the "Available Schemas" list.

2. Never invent new schema names.

3. Do not create any Pydantic models inside routes.py.

4. All request and response schemas must be imported from schemas.py.

5. If a schema is not present in the Available Schemas list, do not use it.

6. Routes.py should only contain:
   - imports
   - APIRouter
   - endpoint functions

7. Do not define BaseModel classes inside routes.py.
IMPORTANT:

1. Use SQLAlchemy ORM directly.

2. Use FastAPI dependency injection.

3. Import:

from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

4. Database access must use:

db: Session = Depends(get_db)

Example:

def get_items(
    db: Session = Depends(get_db)
):
    ...

5. Never assume custom database methods exist.

Do NOT generate code like:

db.create_entity(...)
db.get_entity(...)
db.update_entity(...)
db.delete_entity(...)

6. Use SQLAlchemy ORM operations only:

db.add(...)
db.commit(...)
db.refresh(...)
db.query(...)

7. Generate CRUD logic directly inside route handlers.

8. Do not invent repository, service, manager, or helper methods unless they are explicitly defined in the architecture blueprint.

9. Return only valid FastAPI + SQLAlchemy code.
IMPORTANT:

For GET by id:

obj = db.query(...).filter(...).first()

If obj is None:

raise HTTPException(
    status_code=404,
    detail="<Entity> not found"
)

Never return None for endpoints that use a response_model.



IMPORTANT:

When using a schema:

Only access attributes that exist in that schema.

Example:

If TaskCreate contains:

title
description
completed

Valid:

task.title
task.description
task.completed

Invalid:

task.user_id
task.created_at
task.updated_at

unless those fields exist in the schema.

Never access attributes that are not present in the provided schemas.

Use the provided schemas as the single source of truth.

IMPORTANT:

For authentication endpoints:

If LoginResponse exists:

The /login endpoint response_model must be LoginResponse.

Return data matching LoginResponse exactly.

Example:

return LoginResponse(
    message="Login successful"
)

Never return a User model when response_model is LoginResponse.


IMPORTANT:

Pydantic schemas are request/response validation models.

SQLAlchemy models are database models.

Never add a Pydantic schema instance to the database.

INVALID:

new_user = UserCreate(**user.model_dump())
db.add(new_user)

INVALID:

db.add(user)

VALID:

new_user = User(
    username=user.username,
    email=user.email,
    password=user.password,
    role=user.role
)

db.add(new_user)

Only SQLAlchemy model instances may be passed to:

db.add(...)
db.delete(...)
db.refresh(...)

Request schemas are only used for input validation.



IMPORTANT:

Import SQLAlchemy models from models.py.

Example:

from models import User, Task

When creating database records:

Use SQLAlchemy models.

Never instantiate Create schemas inside route handlers.
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