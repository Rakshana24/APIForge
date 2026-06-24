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

                    forbidden_patterns = []

                    for pattern in forbidden_patterns:

                        if pattern in source:

                            errors.append(
                                f"Test file contains forbidden pattern: {pattern}"
                            )


                    if "uuid.uuid4()" not in source and "uuid4()" not in source:

                        errors.append(
                            "Test file does not generate unique test data"
                        )

                    bad_fields = []

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

                    try:
                        tree = ast.parse(source)
                    except Exception as e:
                        errors.append(f"routes.py: Syntax Error: {e}")
                        tree = None
                        
                    if tree:
                        has_router = False
                        has_models_import = False
                        has_schemas_import = False

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                is_sqlalchemy = False
                                is_pydantic = False
                                for base in node.bases:
                                    base_name = ""
                                    if isinstance(base, ast.Name):
                                        base_name = base.id
                                    elif isinstance(base, ast.Attribute):
                                        base_name = base.attr
                                    
                                    if base_name == "Base":
                                        is_sqlalchemy = True
                                    elif base_name == "BaseModel":
                                        is_pydantic = True
                                
                                has_tablename = any(
                                    isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__tablename__" for t in n.targets)
                                    for n in node.body
                                )
                                if has_tablename or is_sqlalchemy:
                                    errors.append("routes.py contains SQLAlchemy model definitions")
                                if is_pydantic:
                                    errors.append("routes.py contains Pydantic schema definitions")

                            target_names = []
                            value_node = None
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        target_names.append(target.id)
                                value_node = node.value
                            elif isinstance(node, ast.AnnAssign):
                                if isinstance(node.target, ast.Name):
                                    target_names.append(node.target.id)
                                value_node = node.value

                            if value_node:
                                if "router" in target_names:
                                    if isinstance(value_node, ast.Call):
                                        call_func = value_node.func
                                        call_name = ""
                                        if isinstance(call_func, ast.Name):
                                            call_name = call_func.id
                                        elif isinstance(call_func, ast.Attribute):
                                            call_name = call_func.attr
                                        if call_name == "APIRouter":
                                            has_router = True
                                if "app" in target_names:
                                    if isinstance(value_node, ast.Call):
                                        call_func = value_node.func
                                        call_name = ""
                                        if isinstance(call_func, ast.Name):
                                            call_name = call_func.id
                                        elif isinstance(call_func, ast.Attribute):
                                            call_name = call_func.attr
                                        if call_name == "FastAPI":
                                            errors.append("routes.py should use APIRouter, not FastAPI app")

                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    if "models" in name.name:
                                        has_models_import = True
                                    if "schemas" in name.name:
                                        has_schemas_import = True
                            if isinstance(node, ast.ImportFrom) and node.module:
                                if "models" in node.module:
                                    has_models_import = True
                                if "schemas" in node.module:
                                    has_schemas_import = True

                        if not has_router:
                            errors.append("router object missing in routes.py")
                        if not has_models_import:
                            errors.append("routes.py must import models from models.py")
                        if not has_schemas_import:
                            errors.append("routes.py must import schemas from schemas.py")

                    if "Base.metadata.create_all" in source:
                        errors.append("routes.py should not create database tables")
                    if "app = FastAPI()" in source:
                        errors.append("routes.py should use APIRouter, not FastAPI app")

                    if "datetime.now()" in source:
                        if "from datetime import datetime" not in source and "import datetime" not in source:
                            errors.append(
                                "routes.py: datetime.now() used without importing datetime"
                            )

                    if "from main import app" in source:
                        errors.append(
                            "Circular import detected in routes.py"
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
                # -------------------------
                # MAIN VALIDATION
                # -------------------------

                if file == "main.py":

                    if not re.search(r"app\.include_router\(\s*router\s*\)", source):

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

                    if re.search(r"\bcreated_at\s*=\s*Column", source):

                        if not re.search(r"default\s*=\s*datetime\.utcnow", source):

                            errors.append(
                                "models.py: created_at missing default=datetime.utcnow"
                            )

                    if re.search(r"\bupdated_at\s*=\s*Column", source):

                        if not re.search(r"onupdate\s*=\s*datetime\.utcnow", source):

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

                    if not re.search(r"from_attributes\s*=\s*True", source):

                        errors.append(
                            "schemas.py: from_attributes=True missing"
                        )

                    if re.search(r"\bLoginRequest\b", source):

                        if "password" not in source:

                            errors.append(
                                "schemas.py: LoginRequest missing password"
                            )

                    if re.search(r"\bLoginResponse\b", source):

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



