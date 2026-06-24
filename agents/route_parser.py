import re
import ast

def get_node_source(node):
    if hasattr(ast, 'unparse'):
        return ast.unparse(node)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{get_node_source(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return get_node_source(node.func)
    return ""

def extract_route_contracts(routes_code):
    contracts = []
    try:
        tree = ast.parse(routes_code)
    except Exception as e:
        print("AST parsing error in extract_route_contracts:", e)
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    func_node = decorator.func
                    method = None
                    if isinstance(func_node, ast.Attribute):
                        method = func_node.attr.upper()
                    elif isinstance(func_node, ast.Name):
                        method = func_node.id.upper()
                        
                    if method in ["GET", "POST", "PUT", "DELETE"]:
                        if decorator.args and isinstance(decorator.args[0], (ast.Constant, ast.Str)):
                            path = getattr(decorator.args[0], 'value', getattr(decorator.args[0], 's', ''))
                            
                            path_params = re.findall(r"\{([^}]+)\}", path)
                            query_params = []
                            all_args = node.args.args + node.args.kwonlyargs
                            
                            for arg in all_args:
                                arg_name = arg.arg
                                if arg_name in ["db", "current_user"]:
                                    continue
                                if arg_name in path_params:
                                    continue
                                    
                                is_query = True
                                
                                if arg.annotation:
                                    ann_str = get_node_source(arg.annotation)
                                    if "Session" in ann_str or "Depends" in ann_str:
                                        is_query = False
                                        
                                num_args = len(node.args.args)
                                num_defaults = len(node.args.defaults)
                                try:
                                    arg_idx = node.args.args.index(arg)
                                    if arg_idx >= num_args - num_defaults:
                                        default_node = node.args.defaults[arg_idx - (num_args - num_defaults)]
                                        default_str = get_node_source(default_node)
                                        if "Depends" in default_str or "Session" in default_str:
                                            is_query = False
                                except ValueError:
                                    try:
                                        kw_idx = node.args.kwonlyargs.index(arg)
                                        default_node = node.args.kw_defaults[kw_idx]
                                        if default_node:
                                            default_str = get_node_source(default_node)
                                            if "Depends" in default_str or "Session" in default_str:
                                                is_query = False
                                    except ValueError:
                                        pass
                                        
                                if is_query:
                                    query_params.append(arg_name)
                                    
                            contracts.append({
                                "function_name": node.name,
                                "method": method,
                                "path": path,
                                "path_params": path_params,
                                "query_params": query_params
                            })
                            
    print("\nEXTRACTED ROUTE CONTRACTS:")
    for c in contracts:
        print(c)
    return contracts