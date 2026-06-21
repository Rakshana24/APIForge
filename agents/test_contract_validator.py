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

    urls = re.findall(
        r'client\.(?:get|post|put|delete)\("([^"]+)',
        test_code
    )

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