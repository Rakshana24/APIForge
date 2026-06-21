import re


def extract_route_contracts(routes_code):

    contracts = []

    # Works for:
    # @router.get("/books")
    # @router.get("/books", response_model=...)
    # @router.get(
    #     "/books",
    #     response_model=...
    # )

    route_pattern = (
        r'@router\.(get|post|put|delete)\(\s*"([^"]+)"'
    )

    # Supports:
    # def function(...)
    # async def function(...)

    function_pattern = (
        r'(?:async\s+)?def\s+(\w+)\((.*?)\):'
    )

    routes = re.findall(
        route_pattern,
        routes_code,
        re.DOTALL
    )

    functions = re.findall(
        function_pattern,
        routes_code,
        re.DOTALL
    )

    print("\nROUTES FOUND:")
    print(routes)

    print("\nFUNCTIONS FOUND:")
    print(functions)

    for route, func in zip(routes, functions):

        method, path = route

        function_name, params = func

        query_params = []
        path_params = []

        # Extract path params
        if "{" in path:

            path_params = re.findall(
                r"{(.*?)}",
                path
            )

        # Extract query params
        for param in params.split(","):

            param = param.strip()

            if not param:
                continue

            if (
                ":" in param
                and "Depends" not in param
                and "Session" not in param
            ):

                name = (
                    param.split(":")[0]
                    .strip()
                )

                if name not in path_params:

                    query_params.append(
                        name
                    )

        contracts.append(
            {
                "function": function_name,
                "method": method.upper(),
                "path": path,
                "path_params": path_params,
                "query_params": query_params
            }
        )

    print("\nROUTE CONTRACTS:")
    for contract in contracts:
        print(contract)

    return contracts