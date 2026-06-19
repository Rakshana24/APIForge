def classify_error(error_message):

    error = error_message.lower()

    # Test issues
    if (
        "assertionerror" in error
        or "forbidden pattern" in error
        or "test file contains" in error
    ):
        return "test"

    # Schema issues
    if (
        "responsevalidationerror" in error
        or "field required" in error
        or "input should be" in error
    ):
        return "schema"

    # Database issues
    if (
        "integrityerror" in error
        or "foreign key" in error
        or "not null constraint failed" in error
    ):
        return "model"

    # Route issues
    if (
        "nameerror" in error
        or "attributeerror" in error
        or "typeerror" in error
    ):
        return "route"

    return "route"