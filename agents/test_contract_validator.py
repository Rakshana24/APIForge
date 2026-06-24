import re


def validate_tests_against_contracts(
    test_code,
    route_contracts
):

    errors = []

    allowed_routes = set()

    for contract in route_contracts:

        allowed_routes.add(
            contract["path"].rstrip("/")
        )

    urls = []
    # Match double-quoted strings
    for m in re.finditer(r'client\.(?:get|post|put|delete)\(f?"([^"]*)"', test_code):
        urls.append(m.group(1))
    # Match single-quoted strings
    for m in re.finditer(r'client\.(?:get|post|put|delete)\(f?\'([^\']*)\'', test_code):
        urls.append(m.group(1))

    print("\nALLOWED ROUTES:")
    print(allowed_routes)

    print("\nTEST ROUTES:")
    print(urls)

    for url in urls:

        base_url = (
            url.split("?")[0]
               .rstrip("/")
        )

        matched = False

        for route in allowed_routes:

            route = route.rstrip("/")

            pattern = re.sub(
                r"\{.*?\}",
                r"[^/]+",
                route
            )

            pattern = "^" + pattern + "$"

            if re.match(
                pattern,
                base_url
            ):

                matched = True
                break

        if not matched:

            errors.append(
                f"Test uses unknown route: {base_url}"
            )

    return errors