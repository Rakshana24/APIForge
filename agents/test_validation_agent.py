import ast
import re


def validate_test_code(test_code):

    errors = []

    # --------------------------------
    # Syntax Validation
    # --------------------------------

    try:
        ast.parse(test_code)

    except SyntaxError as e:

        errors.append(
            f"Syntax Error: {e}"
        )

        return errors

    # --------------------------------
    # UUID Inside Assertions
    # --------------------------------

    uuid_assert_pattern = (
        r'assert.*uuid\.uuid4\('
    )

    if re.search(
        uuid_assert_pattern,
        test_code,
        re.MULTILINE
    ):

        errors.append(
            "UUID generated directly inside assertion."
        )

    # --------------------------------
    # Too Many Login Calls
    # --------------------------------

    login_calls = len(
        re.findall(
            r'client\.post\(["\']/login',
            test_code
        )
    )

    if login_calls > 3:

        errors.append(
            f"Too many login calls detected ({login_calls})."
        )



    # --------------------------------
    # Missing Status Code Checks
    # --------------------------------

    response_count = len(
        re.findall(
            r'=\s*client\.',
            test_code
        )
    )

    status_checks = len(
        re.findall(
            r'status_code',
            test_code
        )
    )

    if (
        response_count > 0
        and status_checks == 0
    ):

        errors.append(
            "No status code assertions found."
        )

    # --------------------------------
    # Hardcoded IDs
    # --------------------------------

    hardcoded_id_patterns = [
        r'/\d+"',
        r'/\d+\'',
        r'id\s*=\s*\d+'
    ]

    for pattern in hardcoded_id_patterns:

        if re.search(
            pattern,
            test_code
        ):

            errors.append(
                "Hardcoded ID detected."
            )

            break

    return errors