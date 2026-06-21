def get_affected_files(error_type):

    mapping = {

        "model": [
            "models",
            "schemas",
            "routes",
            "tests"
        ],

        "schema": [
            "schemas",
            "routes",
            "tests"
        ],

        "route": [
            "routes",
            "tests"
        ],

        "test": [
            "tests"
        ],

        "data_contract": [
            "models",
            "schemas",
            "routes",
            "tests"
        ]
    }

    return mapping.get(
        error_type,
        []
    )