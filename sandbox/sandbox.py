import ast
import importlib
import sys
from allowed import allowed_builtins, allowed_objects

class Sandbox:
    def __init__(self, debug=False, additional_allowed_imports=None, allowed_modules=None):
        self.debug = debug
        self.allowed_builtins = allowed_builtins
        self.allowed_objects = allowed_objects

        if allowed_modules:
            self.allowed_objects.update(allowed_modules)
        
        self.defined_functions = {}
        self.defined_variables = set()
        self.function_args = set()
        self.loop_variables = set()
        self.local_variables = set()
        self.imported_modules = set()
        self.imported_objects = set()
        self.alias_mapping = {}
        self.class_instances = {}
        self.safe_globals = {}

    def _debug_print(self, message):
        if self.debug:
            print(message)
    
    def _preprocess_code(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defined_functions[node.name] = node
                self._debug_print(f"Function found: {node.name}")
                for arg in node.args.args:
                    self.function_args.add(arg.arg)
                    self._debug_print(f"  Argument found: {arg.arg}")
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.defined_variables.add(target.id)
                        self._debug_print(f"Variable found: {target.id}")
                    if isinstance(target, ast.Name) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                        self.class_instances[target.id] = node.value.func.id
                        self._debug_print(f"Class instance found: {target.id} = {node.value.func.id}")
            if isinstance(node, ast.For):
                if isinstance(node.target, ast.Name):
                    self.loop_variables.add(node.target.id)
                    self._debug_print(f"Loop variable found: {node.target.id}")
            if isinstance(node, ast.comprehension):
                self.local_variables.add(node.target.id)
                self._debug_print(f"Local variable found: {node.target.id}")

    def _check_node(self, node):
        self._debug_print(f"Checking node: {ast.dump(node)}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    importlib.import_module(alias.name)
                except ImportError:
                    print(f"Error: Missing module: {alias.name}")
                    sys.exit(2)
                if alias.name not in self.allowed_objects:
                    print(f"Error: Restricted module: {alias.name}")
                    sys.exit(3)
                self.imported_modules.add(alias.name)
                if alias.asname:
                    self.alias_mapping[alias.asname] = alias.name
                self._debug_print(f"Module found: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            try:
                importlib.import_module(node.module)
            except ImportError:
                print(f"Error: Missing module: {node.module}")
                sys.exit(2)
            if node.module not in self.allowed_objects:
                print(f"Error: Restricted module: {node.module}")
                sys.exit(3)
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                if alias.name not in self.allowed_objects[node.module]:
                    print(f"Error: Restricted module: {full_name}")
                    sys.exit(3)
                self.imported_objects.add((node.module, alias.name))
                if alias.asname:
                    self.alias_mapping[alias.asname] = alias.name
                self._debug_print(f"Object found: {full_name}")
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                instance_name = node.value.id
                if instance_name in self.class_instances:
                    class_name = self.class_instances[instance_name]
                    module_name = self._get_module_name(class_name)
                    full_name = f"{class_name}.{node.attr}"
                    self._debug_print(f"Checking method: {full_name} against {self.allowed_objects.get(module_name, [])}")
                    if full_name not in self.allowed_objects.get(module_name, []):
                        print(f"Error: Restricted method: {full_name} not in {self.allowed_objects.get(module_name, [])}, {class_name=}, {module_name=}")
                        sys.exit(5)
                else:
                    if node.value.id in self.allowed_objects:
                        full_name = f"{node.value.id}.{node.attr}"
                        if full_name not in self.allowed_objects[node.value.id]:
                            print(f"Error: Restricted attribute: {full_name} from {node.value.id} module")
                            sys.exit(4)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            actual_id = self.alias_mapping.get(node.id, node.id)
            if (actual_id not in self.allowed_builtins and 
                actual_id not in self.defined_functions and 
                actual_id not in self.defined_variables and 
                actual_id not in self.function_args and 
                actual_id not in self.loop_variables and 
                actual_id not in self.local_variables and 
                actual_id not in self.imported_modules and 
                actual_id not in {name for _, name in self.imported_objects}):
                if actual_id in self.safe_globals:  ## Check globals defined in script pages..
                    self.defined_variables.add(actual_id)
                else:
                    self._debug_print(f"Restricted usage of built-in function or module: {node.id}")
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_variables.add(target.id)
                    self._debug_print(f"Variable added: {target.id}")
        if isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                self.loop_variables.add(node.target.id)
                self._debug_print(f"Loop variable added: {node.target.id}")
        if isinstance(node, ast.comprehension):
            self.local_variables.add(node.target.id)
            self._debug_print(f"Local variable added: {node.target.id}")

    def _get_module_name(self, class_name):
        for module, classes in self.allowed_objects.items():
            if class_name in classes:
                return module
        return None

    def compile_and_run(self, source_code):
        tree = ast.parse(source_code)
        self._preprocess_code(tree)
        for node in ast.walk(tree):
            self._check_node(node)

        self.safe_globals = {name: globals()[name] for name in self.allowed_builtins if name in globals()}
        for module in self.imported_modules:
            try:
                self.safe_globals[module] = importlib.import_module(module)
                self._debug_print(f"Adding module to globals: {module}")
            except ImportError as e:
                module_name = str(e).split()[-1]
                print(f"Error: Missing module: {module_name}")
                sys.exit(2)
        for module, obj in self.imported_objects:
            imported_module = importlib.import_module(module)
            self.safe_globals[obj] = getattr(imported_module, obj)
            self._debug_print(f"Adding object to globals: {obj}")
        for alias, actual_name in self.alias_mapping.items():
            self.safe_globals[alias] = self.safe_globals[actual_name]
            self._debug_print(f"Adding alias to globals: {alias} -> {actual_name}")

        for func_name, func_node in self.defined_functions.items():
            func_code = compile(ast.Module(body=[func_node], type_ignores=[]), filename="<ast>", mode="exec")
            exec(func_code, self.safe_globals)
        for var_name in self.defined_variables:
            self.safe_globals[var_name] = self.safe_globals.get(var_name, None)

        try:
            compiled_code = compile(tree, filename="<ast>", mode="exec")
            exec(compiled_code, self.safe_globals, self.safe_globals)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    src = sys.argv[1]
    debug_mode = sys.argv[2].lower() == 'true'
    additional_allowed_modules = sys.argv[3] if len(sys.argv) > 3 else "{}"
    
    allowed_modules = ast.literal_eval(additional_allowed_modules)
    print(f'{additional_allowed_modules=} <br> {allowed_modules=}') if debug_mode else None
    
    sandbox = Sandbox(debug=debug_mode)
    
    ## Check all items of allowed_objects
    for module, objects in eval(allowed_modules).items():
        sandbox.allowed_objects.update({module: objects})
    
    try:
        with open(src, 'r') as file:
            code = file.read()
        sandbox.compile_and_run(code)
        print("Code executed successfully.") if debug_mode else None
        sys.exit(0)
    except ModuleNotFoundError as e:
        missing_module = str(e).split("'")[1]
        print(missing_module)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
