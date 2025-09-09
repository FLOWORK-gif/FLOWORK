#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\scripts\dependency_audit.py
# JUMLAH BARIS : 122
#######################################################################

import os
import re
import ast
try:
    import toml
except ImportError:
    print("ERROR: 'toml' library is not installed. Please run 'poetry install' in your terminal.") # English log
    exit()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMPONENT_BASE_DIRS = ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers', 'formatters']
def get_global_dependencies():
    """
    Reads pyproject.toml to get a list of global dependencies and their correct versions.
    This acts as the master dictionary for the auditor.
    """
    pyproject_path = os.path.join(PROJECT_ROOT, 'pyproject.toml')
    if not os.path.exists(pyproject_path):
        print("[ERROR] pyproject.toml not found!") # English log
        return {}, {}
    print("[INFO] Reading global dependencies from pyproject.toml...") # English log
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        data = toml.load(f)
    deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    dep_map = {}
    for pkg, version_info in deps.items():
        if pkg.lower() == 'python':
            continue
        if isinstance(version_info, dict):
            dep_map[pkg] = f"{pkg}{version_info.get('version', '*')}"
        else:
            dep_map[pkg] = f"{pkg}{version_info}"
    import_to_package_map = {
        "bs4": "beautifulsoup4",
        "PIL": "pillow",
        "google.generativeai": "google-generativeai",
        "selenium": "selenium",
        "webdriver_manager": "webdriver-manager",
        "dotenv": "python-dotenv",
        "mss": "mss",
        "pyaudio": "PyAudio",
        "torch": "torch",
        "torchvision": "torchvision",
        "torchaudio": "torchaudio",
        "transformers": "transformers",
        "diffusers": "diffusers",
        "accelerate": "accelerate",
        "safetensors": "safetensors",
        "sentence_transformers": "sentence-transformers",
        "llama_cpp": "llama-cpp-python",
        "pandas": "pandas",
        "openpyxl": "openpyxl" # Added openpyxl for excel module
    }
    print(f"[SUCCESS] Found {len(dep_map)} global packages.") # English log
    return dep_map, import_to_package_map
def find_imports_in_file(file_path):
    """Parses a Python file using AST and returns a set of imported top-level modules."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"  [WARN] Could not parse {os.path.basename(file_path)}: {e}") # English log
        pass
    return imports
def main():
    print("--- Starting Dependency Audit & Auto-Fix Script ---") # English log
    global_deps, import_map = get_global_dependencies()
    fixed_components = 0
    for base_dir in COMPONENT_BASE_DIRS:
        full_base_path = os.path.join(PROJECT_ROOT, base_dir)
        if not os.path.isdir(full_base_path):
            continue
        print(f"\n--- Scanning Directory: '{base_dir}' ---") # English log
        for component_name in os.listdir(full_base_path):
            component_path = os.path.join(full_base_path, component_name)
            if not os.path.isdir(component_path) or component_name == '__pycache__':
                continue
            found_deps_for_component = set()
            for root, _, files in os.walk(component_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        imports = find_imports_in_file(file_path)
                        for imp in imports:
                            package_name = import_map.get(imp, imp)
                            if package_name in global_deps:
                                found_deps_for_component.add(package_name)
            if found_deps_for_component:
                print(f"[FIXING] -> Component '{component_name}' has undeclared/missing dependencies.") # English log
                fixed_components += 1
                requirements_path = os.path.join(component_path, 'requirements.txt')
                try:
                    with open(requirements_path, 'w', encoding='utf-8') as f:
                        for dep_name in sorted(list(found_deps_for_component)):
                            full_dep_string = global_deps[dep_name]
                            f.write(f"{full_dep_string}\n")
                            print(f"    -> Added '{full_dep_string}' to its new requirements.txt") # English log
                    print(f"[SUCCESS] -> Created/Updated requirements.txt for '{component_name}'.") # English log
                except IOError as e:
                    print(f"[ERROR] -> Could not write requirements.txt for '{component_name}': {e}") # English log
    print("\n--- Audit Complete ---") # English log
    if fixed_components > 0:
        print(f"[SUCCESS] {fixed_components} components were auto-fixed with a new 'requirements.txt'.") # English log
    else:
        print("[SUCCESS] All components appear to have their dependencies in order.") # English log
if __name__ == "__main__":
    main()
