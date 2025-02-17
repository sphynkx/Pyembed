import ast
import sys
import argparse

class InputValidator(ast.NodeVisitor):
    def __init__(self):
        self.valid = True
        self.allowed_types = {
            'int', 'float', 'complex', 'str', 'bool', 'list', 'tuple', 'dict', 'set', 'frozenset', 'range',
            'NoneType', 'Ellipsis', 'type(None)', 'numpy.int8', 'numpy.int16', 'numpy.int32', 'numpy.int64',
            'numpy.uint8', 'numpy.uint16', 'numpy.uint32', 'numpy.uint64', 'numpy.float16', 'numpy.float32',
            'numpy.float64', 'numpy.complex64', 'numpy.complex128', 'numpy.bool_', 'numpy.str_', 'numpy.unicode_',
            'numpy.datetime64', 'numpy.timedelta64'
        }

    def visit_Assign(self, node):
        if not isinstance(node.targets[0], ast.Name):
            self.valid = False
        value_node = node.value
        if isinstance(value_node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            elements = value_node.elts if isinstance(value_node, (ast.List, ast.Tuple, ast.Set)) else value_node.values
            for elem in elements:
                if not isinstance(elem, ast.Constant):
                    self.valid = False
                value_type = type(elem.value).__name__ if hasattr(elem, 'value') else 'Ellipsis'
                if value_type not in self.allowed_types:
                    self.valid = False
        elif isinstance(value_node, ast.Constant):
            value_type = type(value_node.value).__name__
            if value_type not in self.allowed_types:
                self.valid = False
        elif isinstance(value_node, ast.Constant) and value_node.value is Ellipsis:
            pass
        else:
            self.valid = False
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.valid = False
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.valid = False
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.valid = False
        self.generic_visit(node)

    def visit_Import(self, node):
        self.valid = False
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.valid = False
        self.generic_visit(node)

    def visit_Call(self, node):
        self.valid = False
        self.generic_visit(node)

    def validate(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
        except Exception as e:
            self.valid = False
        return self.valid


def validate_input_code(input_code):
    validator = InputValidator()
    if validator.validate(input_code):
        return input_code
    else:
        return ""


def validate_input(param):
    try:
        # Save original value with quotes if it is a string
        original_value = param

        # If the parameter starts and ends with quotes, preserve them
        if param.startswith(("'", '"')) and param.endswith(("'", '"')):
            value = param
        else:
            value = ast.literal_eval(param)

        # Return the original value if it was a string
        return original_value if isinstance(value, str) else value

    except:
        print(f"Error: Invalid input parameter '{param}'.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("params", nargs='+')
    args = parser.parse_args()

    for arg in args.params:
        if '=' in arg:
            key, value = arg.split('=', 1)
            validated_value = validate_input(value)
            if validated_value is not None:
                print(f"{key}={validated_value}")
            else:
                sys.exit(1)
        else:
            print(f"Error: Invalid input parameter '{arg}'.")
            sys.exit(1)
