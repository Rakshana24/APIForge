import json


def build_model_contract(blueprint):
    contract = {}
    models = blueprint.get("models", {})
    relationships = blueprint.get("relationships", [])
    
    for model_name, model_info in models.items():
        fields_dict = model_info.get("fields", {})
        field_names = list(fields_dict.keys())
        field_types = {name: str(typ).lower() for name, typ in fields_dict.items()}
        
        primary_key = ["id"] if "id" in field_names else []
        
        nullable = {}
        for name in field_names:
            if name == "id":
                nullable[name] = False
            elif name in ["description", "due_date"]:
                nullable[name] = True
            else:
                nullable[name] = False
                
        model_relationships = []
        for rel in relationships:
            r_model = rel.get("model") or rel.get("model1") or rel.get("model_name")
            r_related = rel.get("related_model") or rel.get("model2") or rel.get("related_model_name")
            r_fk = rel.get("foreign_key") or rel.get("field1") or rel.get("field_name")
            
            if r_model == model_name or r_related == model_name:
                model_relationships.append({
                    "model": r_model,
                    "related_model": r_related,
                    "foreign_key": r_fk,
                    "relationship_type": rel.get("relationship_type") or "foreign_key"
                })
        
        contract[model_name] = {
            "model_name": model_name,
            "fields": field_names,
            "field_types": field_types,
            "nullable": nullable,
            "primary_key": primary_key,
            "relationships": model_relationships
        }
    return contract