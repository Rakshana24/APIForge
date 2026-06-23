import os
import ast
import re

def validation_agent(project_path="generated_project"):

    errors = []

    required_files = [
        "models.py",
        "database.py",
        "schemas.py",
        "routes.py",
        "main.py"
    ]

    # Check required files

    for file in required_files:

        file_path = os.path.join(
            project_path,
            file
        )

        if not os.path.exists(file_path):

            errors.append(
                f"Missing file: {file}"
            )
    
    # Check Python files

    for root, dirs, files in os.walk(project_path):

        for file in files:

            if not file.endswith(".py"):
                continue

            file_path = os.path.join(
                root,
                file
            )

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    source = f.read()

                # Syntax validation
                ast.parse(source)
                
                # -------------------------
                # TEST VALIDATION
                # -------------------------

                if file.startswith("test_"):

                    forbidden_patterns = [
                        '"message" in response.json()',
                        'response.json()["message"]',
                        "response.json()['message']",

                    ]

                    for pattern in forbidden_patterns:

                        if pattern in source:

                            errors.append(
                                f"Test file contains forbidden pattern: {pattern}"
                            )


                    if "uuid.uuid4()" not in source:

                        errors.append(
                            "Test file does not generate unique test data"
                        )

                    bad_fields = [
                        "message",
                        "created_at",
                        "updated_at"
                    ]

                    for field in bad_fields:

                        if f'response.json()["{field}"]' in source:
                            errors.append(
                                f"Test assumes '{field}' exists in response"
                            )

                        if f"response.json()['{field}']" in source:
                            errors.append(
                                f"Test assumes '{field}' exists in response"
                            )
                    
                # -------------------------
                # ROUTES VALIDATION
                # -------------------------

                if file == "routes.py":

                    if (
                        "datetime.now()" in source and
                        "from datetime import datetime" not in source
                    ):
                        errors.append(
                            "routes.py: datetime.now() used without importing datetime"
                        )

                    if "from main import app" in source:

                        errors.append(
                            "Circular import detected in routes.py"
                        )

                    if "router = APIRouter()" not in source:

                        errors.append(
                            "router object missing in routes.py"
                        )

                    if "Depends(get_db)" not in source:

                        errors.append(
                            "routes.py: Depends(get_db) missing"
                        )

                    if "response_model=" not in source:

                        errors.append(
                            "routes.py: response_model missing in endpoints"
                        )

                    forbidden_patterns = [
                        "db.create_",
                        "db.get_",
                        "db.update_",
                        "db.delete_"
                    ]

                    for pattern in forbidden_patterns:

                        if pattern in source:

                            errors.append(
                                f"routes.py: invented database method detected -> {pattern}"
                            )
                    model_pattern = r"class\s+\w+\(Base\)"

                    if re.search(model_pattern, source):
                        errors.append(
                            "routes.py contains SQLAlchemy model definitions"
                        )

                    schema_pattern = r"class\s+\w+\(BaseModel\)"

                    if re.search(schema_pattern, source):
                        errors.append(
                            "routes.py contains Pydantic schema definitions"
                        )

                    if "Base.metadata.create_all" in source:
                        errors.append(
                            "routes.py should not create database tables"
                        )

                    if "app = FastAPI()" in source:
                        errors.append(
                            "routes.py should use APIRouter, not FastAPI app"
                    )

                    if "from models import" not in source:
                        errors.append(
                            "routes.py must import models from models.py"
                        )

                    if "from schemas import" not in source:
                        errors.append(
                            "routes.py must import schemas from schemas.py"
                        )
                # -------------------------
                # MAIN VALIDATION
                # -------------------------

                if file == "main.py":

                    if "app.include_router(router)" not in source:

                        errors.append(
                            "main.py: router not included"
                        )

                    if "Base.metadata.create_all" not in source:

                        errors.append(
                            "main.py: database initialization missing"
                        )
                        
                # -------------------------
                # MODELS VALIDATION
                # -------------------------

                if file == "models.py":

                    if "__tablename__" not in source:

                        errors.append(
                            "models.py: __tablename__ missing"
                        )

                    if "primary_key=True" not in source:

                        errors.append(
                            "models.py: primary key missing"
                        )

                    if "created_at" in source:

                        if "default=datetime.utcnow" not in source:

                            errors.append(
                                "models.py: created_at missing default=datetime.utcnow"
                            )

                    if "updated_at" in source:

                        if "onupdate=datetime.utcnow" not in source:

                            errors.append(
                                "models.py: updated_at missing onupdate=datetime.utcnow"
                            )   
                # -------------------------
                # SCHEMA VALIDATION
                # -------------------------

                if file == "schemas.py":

                    if "BaseModel" not in source:

                        errors.append(
                            "schemas.py: BaseModel missing"
                        )

                    if "from_attributes = True" not in source:

                        errors.append(
                            "schemas.py: from_attributes=True missing"
                        )

                    if "LoginRequest" in source:

                        if "password" not in source:

                            errors.append(
                                "schemas.py: LoginRequest missing password"
                            )

                    if "LoginResponse" in source:

                        if (
                            "token" not in source and
                            "message" not in source
                        ):

                            errors.append(
                                "schemas.py: LoginResponse appears empty"
                            )

            except SyntaxError as e:

                errors.append(
                    f"Syntax Error in {file}: {e}"
                )

            except Exception as e:

                errors.append(
                    f"Validation Error in {file}: {e}"
                )

    return errors



