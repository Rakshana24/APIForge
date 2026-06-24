import re

def get_route_function_name(method, path):
    parts = [p for p in path.split("/") if p and not p.startswith("{")]
    if not parts:
        return "root"
        
    entity = parts[-1]
    if entity.endswith("s") and len(entity) > 1:
        entity = entity[:-1]
        
    method = method.lower()
    if method == "post":
        if "login" in path:
            return "login"
        return f"create_{entity}"
    elif method == "get":
        is_singular = path.endswith("}") or "{" in path.split("/")[-1]
        if is_singular:
            return f"read_{entity}"
        else:
            return f"read_{parts[-1]}"
    elif method == "put":
        return f"update_{entity}"
    elif method == "delete":
        return f"delete_{entity}"
    return f"{method}_{'_'.join(parts)}"

def get_entity_name_from_path(path, blueprint):
    models = blueprint.get("models", {})
    parts = [p.lower() for p in path.split("/") if p]
    
    # 1. Exact or plural match
    for model_name in models.keys():
        m_lower = model_name.lower()
        if m_lower in parts or (m_lower + "s") in parts:
            return model_name
            
    # 2. Substring match (e.g. "low_stock" matches "Stock")
    for model_name in models.keys():
        m_lower = model_name.lower()
        if any(m_lower in p for p in parts):
            return model_name
            
    # 3. Fallback to the first model in the blueprint, or "User" if none
    if models:
        return list(models.keys())[0]
    return "User"

def build_route_contract(blueprint):
    contracts = []
    routes = blueprint.get("routes", [])
    for route in routes:
        method = route.get("method", "GET").upper()
        path = route.get("path", "/")
        
        query_params = []
        if "?" in path:
            path_part, query_part = path.split("?", 1)
            path = path_part
            for param_pair in query_part.split("&"):
                if "=" in param_pair:
                    query_params.append(param_pair.split("=")[0])
                else:
                    query_params.append(param_pair)
        
        path_params = re.findall(r"\{([^}]+)\}", path)
        function_name = get_route_function_name(method, path)
        
        entity = get_entity_name_from_path(path, blueprint)
        request_schema = None
        response_schema = None
        
        if "register" in path:
            request_schema = "UserCreate"
            response_schema = "UserResponse"
        elif "login" in path:
            request_schema = "LoginRequest"
            response_schema = "LoginResponse"
        else:
            if method == "POST":
                request_schema = f"{entity}Create"
                response_schema = f"{entity}Response"
            elif method == "PUT":
                request_schema = f"{entity}Update"
                response_schema = f"{entity}Response"
            elif method == "GET":
                is_singular = path.endswith("}") or "{" in path.split("/")[-1]
                if is_singular:
                    response_schema = f"{entity}Response"
                else:
                    response_schema = f"List[{entity}Response]"
            elif method == "DELETE":
                response_schema = "dict"
                
        contracts.append({
            "function_name": function_name,
            "method": method,
            "path": path,
            "path_params": path_params,
            "query_params": query_params,
            "request_schema": request_schema,
            "response_schema": response_schema
        })
    return contracts
