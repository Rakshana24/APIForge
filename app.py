import json
import os
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
    save_schema_contract
)
from agents.test_syntax_validator import (
    validate_test_syntax
)
from agents.test_contract_validator import (
    validate_tests_against_contracts
)
from agents.route_parser import (
    extract_route_contracts
)
from agents.test_repair_agent import(
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

user_requirement = input("Requirement: ")

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


# Requirement Agent
specification = requirement_agent(final_requirement)

print("\n========== SPECIFICATION ==========")
print(json.dumps(specification, indent=4))

# Architecture Agent
blueprint = architecture_agent(specification)

print("\n========== ARCHITECTURE ==========")
print(json.dumps(blueprint, indent=4))

models_code = code_generation_agent(blueprint)

models_code = clean_code(models_code)

model_contract = build_model_contract(
    blueprint
)
print(
    "\nMODEL CONTRACT:\n"
)

print(
    json.dumps(
        model_contract,
        indent=4
    )
)

import re

model_names = re.findall(
    r"class\s+(\w+)\(",
    models_code
)

print("\nMODELS FOUND:")
print(model_names)



print("\n========== GENERATED MODELS ==========\n")
print(models_code)
os.makedirs("generated_project", exist_ok=True)
db_path = "generated_project/app.db"

if os.path.exists(db_path):

    os.remove(db_path)

    print("Old database removed!")
with open("generated_project/models.py", "w", encoding="utf-8") as file:
    file.write(models_code)

print("\nmodels.py generated successfully!")
database_code = database_generation_agent()

with open(
    "generated_project/database.py",
    "w",
    encoding="utf-8"
) as file:
    file.write(database_code)

print("database.py generated successfully!")

schemas_code = schema_generation_agent(blueprint, model_contract)
schemas_code = clean_code(schemas_code)
schema_contract = save_schema_contract(
    schemas_code
)
import re

schema_names = re.findall(
    r"class\s+(\w+)\(",
    schemas_code
)

print("\nSCHEMAS FOUND:")
print(schema_names)
with open(
    "generated_project/schemas.py",
    "w",
    encoding="utf-8"
) as file:
    file.write(schemas_code)

print("schemas.py generated successfully!")

routes_code = route_generation_agent(blueprint,schema_contract)
routes_code = clean_code(routes_code)
print("\n========== GENERATED ROUTES ==========\n")
print(routes_code)
route_contracts = (
    extract_route_contracts(
        routes_code
    )
)
if len(route_contracts) == 0:

    print("\nROUTE CONTRACT EXTRACTION FAILED")

    print("\nGENERATED ROUTES:\n")

    print(routes_code)

    raise Exception(
        "Route Contract Extraction Failed"
    )

with open(
    "contracts/route_contract.json",
    "w"
) as f:

    json.dump(
        route_contracts,
        f,
        indent=4
    )

print("\nROUTE CONTRACTS:\n")
print(route_contracts)
with open(
    "generated_project/routes.py",
    "w",
    encoding="utf-8"
) as file:
    file.write(routes_code)

print("routes.py generated successfully!")

test_code = test_generation_agent(
    blueprint,
    schema_contract,
    route_contracts
)
print("\n========== GENERATED TESTS ==========\n")
print(test_code)
from agents.test_repair_agent import repair_test_code

test_code = clean_code(
    test_code
)
valid_syntax, syntax_error = (
    validate_test_syntax(
        test_code
    )
)

if not valid_syntax:

    print(
        "\nTEST SYNTAX VALIDATION FAILED\n"
    )

    print(syntax_error)

    exit()

contract_errors = (
    validate_tests_against_contracts(
        test_code,
        route_contracts
    )
)

if contract_errors:

    print(
        "\nTEST CONTRACT VALIDATION FAILED\n"
    )

    for error in contract_errors:

        print(error)

    exit()
validation_errors = (
    validate_test_code(
        test_code
    )
)

if validation_errors:

    print(
        "\nTEST VALIDATION FAILED\n"
    )

    for error in validation_errors:

        print(error)

    exit()
os.makedirs(
    "generated_project/tests",
    exist_ok=True
)

with open(
    "generated_project/tests/test_api.py",
    "w",
    encoding="utf-8"
) as file:

    file.write(test_code)

print("tests generated successfully!")


main_code = main_generation_agent()
main_code = clean_code(main_code)
with open(
    "generated_project/main.py",
    "w",
    encoding="utf-8"
) as file:

    file.write(main_code)

print("main.py generated successfully!")




print("\nRunning Validation and Execution...\n")

MAX_RETRIES = 3

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

        elif "schemas.py" in error_message:
            target_file = "generated_project/schemas.py"

        elif "models.py" in error_message:
            target_file = "generated_project/models.py"

        else:
            target_file = "generated_project/routes.py"

        original_code = read_file(
            target_file
        )

        fixed_code = repair_agent(
            original_code,
            error_message
        )

        fixed_code = clean_code(
            fixed_code
        )

        with open(
            target_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(fixed_code)

        print("\nValidation repair completed!")

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
            break

        else:

            print("Tests Failed!")

            print("\nSTDOUT:\n")
            print(test_result["stdout"])

            print("\nSTDERR:\n")
            print(test_result["stderr"])

            error_message = (
                test_result["stdout"]
                + "\n"
                + test_result["stderr"]
            )
            error_message = compress_error(
                error_message
            )

            original_test_code = read_file(
                "generated_project/tests/test_api.py"
            )

            error_type = classify_error(error_message)

            print(f"\nDetected Error Type: {error_type}")
            affected_files = get_affected_files(
                error_type
            )

            print(
                f"\nAffected Files: {affected_files}"
            )
            if error_type == "data_contract":

                print(
                    "\nData Contract Error Detected."
                )

                print(
                    "\nRegenerating Tests...\n"
                )

                test_code = test_generation_agent(
                blueprint,
                schemas_code,
                routes_code,
                route_contracts
                )

                test_code = clean_code(
                test_code
                )

                with open(
                    "generated_project/tests/test_api.py",
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(test_code)

                continue

            if error_type == "test":

                original_test_code = read_file(
                    "generated_project/tests/test_api.py"
                )

                fixed_test_code = repair_test_code(
                    original_test_code,
                    error_message,
                    route_contracts,
                    schemas_code
                )

                with open(
                    "generated_project/tests/test_api.py",
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(
                        clean_code(fixed_test_code)
                    )
                print("\nTEST REPAIR COMPLETED\n")

            else:

                if error_type == "schema":
                    target_file = "generated_project/schemas.py"

                elif error_type == "model":
                    target_file = "generated_project/models.py"

                else:
                    target_file = "generated_project/routes.py"

                original_code = read_file(
                    target_file
                )

                fixed_code = repair_agent(
                    original_code,
                    error_message
                )

                with open(
                    target_file,
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(
                        clean_code(fixed_code)
                    )

                print("\nRepair completed!")
            continue

            

    print("Execution Failed!")

    print("\nSTDERR:\n")
    print(execution_result["stderr"])

    # -----------------------------
    # REPAIR
    # -----------------------------

    error_message = compress_error(
        execution_result["stderr"]
    )
    

    target_file = "generated_project/routes.py"

    original_code = read_file(
        target_file
    )

    fixed_code = repair_agent(
        original_code,
        error_message
    )

    fixed_code = clean_code(
        fixed_code
    )

    with open(
        target_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(fixed_code)

    print("\nRepair completed!")

else:

    print(
        "\nMaximum repair attempts reached."
    )
