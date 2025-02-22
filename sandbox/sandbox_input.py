import ast
import sys
import base64

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
        self.visit_value(value_node)
        self.generic_visit(node)

    def visit_value(self, value_node):
        if isinstance(value_node, (ast.List, ast.Tuple, ast.Set)):
            elements = value_node.elts
            for elem in elements:
                if not isinstance(elem, (ast.Constant, ast.List, ast.Tuple, ast.Set)):
                    self.valid = False
                else:
                    value_type = type(elem.value).__name__ if hasattr(elem, 'value') else 'Ellipsis'
                    if value_type not in self.allowed_types:
                        self.valid = False
                if isinstance(elem, (ast.List, ast.Tuple, ast.Set)):
                    self.visit_value(elem)
        elif isinstance(value_node, ast.Dict):
            for key, value in zip(value_node.keys, value_node.values):
                if not isinstance(key, ast.Constant) or not isinstance(value, (ast.Constant, ast.List, ast.Tuple, ast.Set)):
                    self.valid = False
                if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                    self.visit_value(value)
        elif isinstance(value_node, ast.Constant):
            value_type = type(value_node.value).__name__
            if value_type not in self.allowed_types:
                self.valid = False
        elif isinstance(value_node, ast.Constant) and value_node.value is Ellipsis:
            pass
        else:
            self.valid = False

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

if __name__ == "__main__":
    encoded_input = sys.argv[1]
    input_code = base64.b64decode(encoded_input).decode('utf-8')
    validated_code = validate_input_code(input_code)
    if validated_code:
        print(validated_code)
    else:
        sys.exit(1)
