def repair_test_code(test_code):

    test_code = test_code.replace(
        'assert "message" in response.json()',
        ''
    )

    test_code = test_code.replace(
        'response.json()["message"]',
        'response.json()'
    )

    test_code = test_code.replace(
        "response.json()['message']",
        "response.json()"
    )

    test_code = test_code.replace(
        "datetime.now()",
        "datetime.now().isoformat()"
    )
    test_code = test_code.replace(
    ".isoformat().isoformat()",
    ".isoformat()"
    )

    return test_code