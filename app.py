import json
import os
import sys
from agents.validation_agent import validation_agent
from agents.error_classifier import classify_error
from agents.execution_agent import execution_agent
from agents.code_generation_agent import (
    code_generation_agent,
    database_generation_agent,
    schema_generation_agent,
    route_generation_agent,
    main_generation_agent
)
from agents.test_validation_agent import (
    validate_test_code
)
from contracts.model_contract import (
    build_model_contract
)
from contracts.schema_contract import (
    build_schema_contract
)
from contracts.route_contract import (
    build_route_contract
)
from agents.test_syntax_validator import (
    validate_test_syntax
)
from agents.test_contract_validator import (
    validate_tests_against_contracts
)
from agents.test_repair_agent import (
    repair_test_code
)
from agents.test_generation_agent import (
    test_generation_agent
)
from agents.test_execution_agent import (
    test_execution_agent
)
from agents.dependency_mapper import (
    get_affected_files
)
from agents.clarification_agent import clarification_agent
from agents.requirement_agent import requirement_agent
from agents.architecture_agent import architecture_agent
from agents.repair_agent import repair_agent

def read_file(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()

def clean_code(code):
    code = code.replace("```python", "")
    code = code.replace("```", "")
    code = code.strip()
    return code

def compress_error(error):
    keywords = [
        "IntegrityError",
        "NOT NULL",
        "ResponseValidationError",
        "422",
        "404",
        "AttributeError",
        "NameError",
        "TypeError"
    ]
    lines = []
    for line in error.splitlines():
        if any(
            keyword.lower() in line.lower()
            for keyword in keywords
        ):
            lines.append(line)
    return "\n".join(lines[:10])

def log_repair(error_type, affected_file, before_code, after_code):
    log_entry = {
        "error_type": error_type,
        "affected_file": affected_file,
        "before_repair": before_code,
        "after_repair": after_code
    }
    with open("repair_observability.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def regenerate_dependents(changed_file, blueprint, model_contract, schema_contract, route_contracts):
    if changed_file == "models":
        print("Dependency-Aware Regeneration: Models changed. Regenerating Schemas, Routes, Tests...")
        schemas_code = schema_generation_agent(schema_contract)
        schemas_code = clean_code(schemas_code)
        with open("generated_project/schemas.py", "w", encoding="utf-8") as file:
            file.write(schemas_code)
            
        routes_code = route_generation_agent(route_contracts, schema_contract, model_contract)
        routes_code = clean_code(routes_code)
        with open("generated_project/routes.py", "w", encoding="utf-8") as file:
            file.write(routes_code)
            
        test_code = test_generation_agent(route_contracts, schema_contract)
        test_code = clean_code(test_code)
        with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
            file.write(test_code)
            
    elif changed_file == "schemas":
        print("Dependency-Aware Regeneration: Schemas changed. Regenerating Routes, Tests...")
        routes_code = route_generation_agent(route_contracts, schema_contract, model_contract)
        routes_code = clean_code(routes_code)
        with open("generated_project/routes.py", "w", encoding="utf-8") as file:
            file.write(routes_code)
            
        test_code = test_generation_agent(route_contracts, schema_contract)
        test_code = clean_code(test_code)
        with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
            file.write(test_code)
            
    elif changed_file == "routes":
        print("Dependency-Aware Regeneration: Routes changed. Regenerating Tests...")
        test_code = test_generation_agent(route_contracts, schema_contract)
        test_code = clean_code(test_code)
        with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
            file.write(test_code)

def run_api_forge(user_requirement, answers=None):
    if answers is None:
        questions = clarification_agent(user_requirement)
        if "NO_QUESTIONS" not in questions:
            print("\nClarification Questions:\n")
            print(questions)
            answers = input("\nEnter answers (combined): ")
            final_requirement = f"""
{user_requirement}

Additional Information:
{answers}
"""
        else:
            final_requirement = user_requirement
    else:
        if answers:
            final_requirement = f"""
{user_requirement}

Additional Information:
{answers}
"""
        else:
            final_requirement = user_requirement

    # Requirement Agent
    specification = requirement_agent(final_requirement)
    print("\n========== SPECIFICATION ==========")
    print(json.dumps(specification, indent=4))

    # Architecture Agent
    blueprint = architecture_agent(specification)
    blueprint["authentication"] = specification.get("authentication", False)
    blueprint["specification"] = specification
    print("\n========== ARCHITECTURE ==========")
    print(json.dumps(blueprint, indent=4))

    # Phase 1: Build Contracts BEFORE code generation
    model_contract = build_model_contract(blueprint)
    os.makedirs("contracts", exist_ok=True)
    with open("contracts/model_contract.json", "w") as f:
        json.dump(model_contract, f, indent=4)
        
    schema_contract = build_schema_contract(blueprint, model_contract)
    with open("contracts/schema_contract.json", "w") as f:
        json.dump(schema_contract, f, indent=4)
        
    route_contracts = build_route_contract(blueprint)
    with open("contracts/route_contract.json", "w") as f:
        json.dump(route_contracts, f, indent=4)

    print("\nMODEL CONTRACT:\n", json.dumps(model_contract, indent=4))
    print("\nSCHEMA CONTRACT:\n", json.dumps(schema_contract, indent=4))
    print("\nROUTE CONTRACTS:\n", json.dumps(route_contracts, indent=4))

    # Code generation - Models
    models_code = code_generation_agent(model_contract)
    models_code = clean_code(models_code)
    
    os.makedirs("generated_project", exist_ok=True)
    db_path = "generated_project/app.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Old database removed!")
        
    with open("generated_project/models.py", "w", encoding="utf-8") as file:
        file.write(models_code)
    print("\nmodels.py generated successfully!")

    # Database code
    database_code = database_generation_agent()
    with open("generated_project/database.py", "w", encoding="utf-8") as file:
        file.write(database_code)
    print("database.py generated successfully!")

    # Schemas code (consuming schema_contract)
    schemas_code = schema_generation_agent(schema_contract)
    schemas_code = clean_code(schemas_code)
    with open("generated_project/schemas.py", "w", encoding="utf-8") as file:
        file.write(schemas_code)
    print("schemas.py generated successfully!")

    # Routes code (consuming route_contracts)
    routes_code = route_generation_agent(route_contracts, schema_contract, model_contract)
    routes_code = clean_code(routes_code)
    with open("generated_project/routes.py", "w", encoding="utf-8") as file:
        file.write(routes_code)
    print("routes.py generated successfully!")

    # Tests code (consuming route_contracts)
    test_code = test_generation_agent(route_contracts, schema_contract)
    test_code = clean_code(test_code)

    # Test validation and repair before writing
    MAX_TEST_REPAIR_ATTEMPTS = 3
    for attempt in range(MAX_TEST_REPAIR_ATTEMPTS):
        # 1. Syntax Validation
        valid_syntax, syntax_error = validate_test_syntax(test_code)
        if not valid_syntax:
            print(f"\nTEST SYNTAX VALIDATION FAILED (Attempt {attempt + 1})\n", syntax_error)
            if attempt == MAX_TEST_REPAIR_ATTEMPTS - 1:
                raise Exception(f"Test Syntax Validation Failed: {syntax_error}")
            test_code = repair_test_code(test_code, f"Syntax Error: {syntax_error}", route_contracts, schemas_code)
            test_code = clean_code(test_code)
            continue

        # 2. Contract Validation
        contract_errors = validate_tests_against_contracts(test_code, route_contracts)
        if contract_errors:
            print(f"\nTEST CONTRACT VALIDATION FAILED (Attempt {attempt + 1})\n")
            for error in contract_errors:
                print(error)
            if attempt == MAX_TEST_REPAIR_ATTEMPTS - 1:
                raise Exception(f"Test Contract Validation Failed: {contract_errors}")
            error_message = "\n".join(contract_errors)
            test_code = repair_test_code(test_code, error_message, route_contracts, schemas_code)
            test_code = clean_code(test_code)
            continue

        # 3. Static/Rules Validation
        validation_errors = validate_test_code(test_code)
        if validation_errors:
            print(f"\nTEST VALIDATION FAILED (Attempt {attempt + 1})\n")
            for error in validation_errors:
                print(error)
            if attempt == MAX_TEST_REPAIR_ATTEMPTS - 1:
                raise Exception(f"Test Validation Failed: {validation_errors}")
            error_message = "\n".join(validation_errors)
            test_code = repair_test_code(test_code, error_message, route_contracts, schemas_code)
            test_code = clean_code(test_code)
            continue

        # If we reach here, all validations passed!
        print("\nTest validation passed successfully!")
        break

    os.makedirs("generated_project/tests", exist_ok=True)
    with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
        file.write(test_code)
    print("tests generated successfully!")

    # Main code
    main_code = main_generation_agent()
    main_code = clean_code(main_code)
    with open("generated_project/main.py", "w", encoding="utf-8") as file:
        file.write(main_code)
    print("main.py generated successfully!")

    print("\nRunning Validation and Execution...\n")
    MAX_RETRIES = 3
    success = False

    for attempt in range(MAX_RETRIES):
        print(f"\n========== ATTEMPT {attempt + 1} ==========\n")

        # -----------------------------
        # VALIDATION
        # -----------------------------
        errors = validation_agent()
        if errors:
            print("Validation Failed!\n")
            for error in errors:
                print(error)
            error_message = "\n".join(errors)

            if "routes.py" in error_message:
                target_file = "generated_project/routes.py"
                changed = "routes"
            elif "schemas.py" in error_message:
                target_file = "generated_project/schemas.py"
                changed = "schemas"
            elif "models.py" in error_message:
                target_file = "generated_project/models.py"
                changed = "models"
            else:
                target_file = "generated_project/routes.py"
                changed = "routes"

            original_code = read_file(target_file)
            
            print(f"\n--- BEFORE REPAIR ({target_file}) ---")
            print(original_code)
            
            fixed_code = repair_agent(original_code, error_message)
            fixed_code = clean_code(fixed_code)
            
            print(f"\n--- AFTER REPAIR ({target_file}) ---")
            print(fixed_code)
            
            log_repair(classify_error(error_message), target_file, original_code, fixed_code)

            with open(target_file, "w", encoding="utf-8") as file:
                file.write(fixed_code)

            print("\nValidation repair completed!")
            regenerate_dependents(changed, blueprint, model_contract, schema_contract, route_contracts)
            continue

        print("Validation Passed!")

        # -----------------------------
        # EXECUTION
        # -----------------------------
        print("\nRunning Execution Agent...\n")
        execution_result = execution_agent()
        if execution_result["success"]:
            print("Execution Passed!")
            print("\nRunning Test Execution Agent...\n")
            test_result = test_execution_agent()
            if test_result["success"]:
                print("All Tests Passed!")
                success = True
                break
            else:
                print("Tests Failed!")
                print("\nSTDOUT:\n", test_result["stdout"])
                print("\nSTDERR:\n", test_result["stderr"])

                error_message = test_result["stdout"] + "\n" + test_result["stderr"]
                error_message = compress_error(error_message)

                error_type = classify_error(error_message)
                print(f"\nDetected Error Type: {error_type}")
                affected_files = get_affected_files(error_type)
                print(f"\nAffected Files: {affected_files}")

                if error_type == "data_contract":
                    print("\nData Contract Error Detected. Regenerating Tests...\n")
                    test_code = test_generation_agent(route_contracts, schema_contract)
                    test_code = clean_code(test_code)
                    with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
                        file.write(test_code)
                    continue

                if error_type == "test":
                    original_test_code = read_file("generated_project/tests/test_api.py")
                    
                    print("\n--- BEFORE REPAIR (generated_project/tests/test_api.py) ---")
                    print(original_test_code)
                    
                    fixed_test_code = repair_test_code(original_test_code, error_message, route_contracts, schemas_code)
                    fixed_test_code = clean_code(fixed_test_code)
                    
                    print("\n--- AFTER REPAIR (generated_project/tests/test_api.py) ---")
                    print(fixed_test_code)
                    
                    log_repair("test", "generated_project/tests/test_api.py", original_test_code, fixed_test_code)

                    with open("generated_project/tests/test_api.py", "w", encoding="utf-8") as file:
                        file.write(fixed_test_code)
                    print("\nTEST REPAIR COMPLETED\n")
                else:
                    if error_type == "schema":
                        target_file = "generated_project/schemas.py"
                        changed = "schemas"
                    elif error_type == "model":
                        target_file = "generated_project/models.py"
                        changed = "models"
                    else:
                        target_file = "generated_project/routes.py"
                        changed = "routes"

                    original_code = read_file(target_file)
                    
                    print(f"\n--- BEFORE REPAIR ({target_file}) ---")
                    print(original_code)
                    
                    fixed_code = repair_agent(original_code, error_message)
                    fixed_code = clean_code(fixed_code)
                    
                    print(f"\n--- AFTER REPAIR ({target_file}) ---")
                    print(fixed_code)
                    
                    log_repair(error_type, target_file, original_code, fixed_code)

                    with open(target_file, "w", encoding="utf-8") as file:
                        file.write(fixed_code)
                        
                    print("\nRepair completed!")
                    regenerate_dependents(changed, blueprint, model_contract, schema_contract, route_contracts)
                continue
        else:
            print("Execution Failed!")
            print("\nSTDERR:\n", execution_result["stderr"])
            
            error_message = compress_error(execution_result["stderr"])
            target_file = "generated_project/routes.py"
            original_code = read_file(target_file)
            
            print(f"\n--- BEFORE REPAIR ({target_file}) ---")
            print(original_code)
            
            fixed_code = repair_agent(original_code, error_message)
            fixed_code = clean_code(fixed_code)
            
            print(f"\n--- AFTER REPAIR ({target_file}) ---")
            print(fixed_code)
            
            log_repair(classify_error(error_message), target_file, original_code, fixed_code)

            with open(target_file, "w", encoding="utf-8") as file:
                file.write(fixed_code)
            print("\nRepair completed!")
            regenerate_dependents("routes", blueprint, model_contract, schema_contract, route_contracts)
            continue
    else:
        final_validation_errors = validation_agent()
        if final_validation_errors:
            raise Exception(f"Validation failed after max retries: {final_validation_errors}")
        else:
            raise Exception("Maximum repair attempts reached without resolving all test execution failures.")

    return success

if __name__ == "__main__":
    user_requirement = input("Requirement: ")
    try:
        run_api_forge(user_requirement)
    except Exception as e:
        print(f"\nAPIForge execution stopped due to failure: {e}")
        sys.exit(1)
