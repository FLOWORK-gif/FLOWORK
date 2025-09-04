import ast
import os

class RefactorEngine(ast.NodeTransformer):
    """
    The core engine for finding and fixing architectural issues in code using AST.
    It works by traversing the code's abstract syntax tree and applying transformations.

    Think of it as a surgical tool for code, not a simple find-and-replace.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.content_changed = False
        self.findings = []

        # Read the source code
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.source_code = f.read()

    def analyze(self):
        """
        Parses the code into an AST and runs the analysis.
        This is the diagnostic step.
        """
        try:
            tree = ast.parse(self.source_code)
            # In the future, we will have multiple visitor classes for different rules.
            # For now, we start with one.
            visitor = GetServiceVisitor()
            visitor.visit(tree)
            self.findings = visitor.findings
        except Exception as e:
            print(f"[ERROR] Could not parse or analyze file {self.file_path}: {e}")

    def apply_fixes(self):
        """
        Applies the necessary transformations to the code and writes it back.
        This is the surgical step.
        """
        # This will be implemented in our next mission.
        # The logic will involve creating a NodeTransformer to rewrite the AST
        # and then using ast.unparse() to generate the new code.
        print("Auto-fixing logic is not implemented yet.")
        pass

class GetServiceVisitor(ast.NodeVisitor):
    """
    An AST visitor specifically designed to find '.kernel.get_service()' calls.
    """
    def __init__(self):
        self.findings = []
        self._current_method = None

    def visit_FunctionDef(self, node):
        """Keep track of which method we are currently inside."""
        self._current_method = node.name
        self.generic_visit(node)
        self._current_method = None

    def visit_Call(self, node):
        """This method is called for every function call in the code."""
        # Check if this is a call like `something.get_service`
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'get_service':
            # Check if it's being called on an attribute named 'kernel'
            if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'kernel':
                finding = {
                    "line": node.lineno,
                    "method": self._current_method,
                    "message": f"Direct call to '.kernel.get_service()' found in method '{self._current_method}'."
                }
                self.findings.append(finding)

        # Continue traversing the tree
        self.generic_visit(node)

# This part is for standalone testing of this file
if __name__ == '__main__':
    # We point it to a known problematic file for our test
    # Note: The path is relative to this file's location
    target_file = '../../flowork_kernel/ui_shell/properties_popup.py'

    if os.path.exists(target_file):
        engine = RefactorEngine(target_file)
        engine.analyze()

        if engine.findings:
            print(f"Found {len(engine.findings)} issues in {os.path.basename(target_file)}:")
            for find in engine.findings:
                print(f"  - Line {find['line']}: {find['message']}")
        else:
            print(f"No issues found in {os.path.basename(target_file)}.")
    else:
        print(f"Test file not found: {target_file}")