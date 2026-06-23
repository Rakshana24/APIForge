import re
import json

def save_schema_contract(schemas_code):

    contract = {}

    classes = re.findall(
        r'class\s+(\w+)\(.*?\):(.*?)(?=class|\Z)',
        schemas_code,
        re.S
    )

    for schema_name, body in classes:

        fields = re.findall(
            r'^\s*(\w+)\s*:',
            body,
            re.M
        )

        contract[schema_name] = fields

    with open(
        "contracts/schema_contract.json",
        "w"
    ) as f:

        json.dump(
            contract,
            f,
            indent=4
        )

    return contract