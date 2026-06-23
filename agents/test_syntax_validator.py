import ast

def validate_test_syntax(test_code):

    try:
        ast.parse(test_code)
        return True, None

    except SyntaxError as e:
        return False, str(e)