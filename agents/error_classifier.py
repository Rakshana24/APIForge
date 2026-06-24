def classify_error(error_message):

    error = error_message.lower()

    # -----------------------------
    # SPECIFIC DATA CONTRACT / DB / SCHEMA / ROUTE ISSUES FIRST
    # -----------------------------

    if (
        "invalid keyword argument" in error
        or "responsevalidationerror" in error
        or "field required" in error
        or "not null constraint failed" in error
        or "422" in error
        or "unprocessable entity" in error
    ):
        return "data_contract"

    if (
        "integrityerror" in error
        or "foreign key" in error
    ):
        return "model"

    if (
        "input should be" in error
    ):
        return "schema"

    if (
        "attributeerror" in error
        or "typeerror" in error
        or "nameerror" in error
    ):
        return "route"

    # -----------------------------
    # FILE-BASED & GENERIC FALLBACK DETECTION
    # -----------------------------

    if "models.py" in error:
        return "model"

    if "schemas.py" in error:
        return "schema"

    if "routes.py" in error:
        return "route"

    if "test_api.py" in error:
        return "test"

    if (
        "assertionerror" in error
        or "forbidden pattern" in error
        or "test file contains" in error
        or "404 not found" in error
    ):
        return "test"

    return "route"