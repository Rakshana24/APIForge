import json

def build_schema_contract(blueprint, model_contract):
    contract = {
        "Create Schemas": {},
        "Update Schemas": {},
        "Response Schemas": {},
        "Authentication Schemas": {}
    }
    
    for model_name, model_info in model_contract.items():
        fields = model_info.get("fields", [])
        
        # Create schema: exclude id, created_at, updated_at
        create_fields = [f for f in fields if f not in ["id", "created_at", "updated_at"]]
        contract["Create Schemas"][f"{model_name}Create"] = create_fields
        
        # Update schema: same fields as Create
        contract["Update Schemas"][f"{model_name}Update"] = create_fields
        
        # Response schema: include id, exclude password, password_hash
        response_fields = []
        if "id" in fields:
            response_fields.append("id")
        for f_name in fields:
            if f_name not in ["password", "password_hash", "id"]:
                response_fields.append(f_name)
        for extra in ["created_at", "updated_at"]:
            if extra in fields and extra not in response_fields:
                response_fields.append(extra)
        contract["Response Schemas"][f"{model_name}Response"] = response_fields
        
    if blueprint.get("authentication") or blueprint.get("specification", {}).get("authentication"):
        contract["Authentication Schemas"]["LoginRequest"] = ["username", "password"]
        contract["Authentication Schemas"]["LoginResponse"] = ["message"]
        
    return contract