#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\dependency_audit.py
# (File baru untuk audit dependensi)
#######################################################################

import os
import re
import ast
try:
    import toml
except ImportError:
    print("ERROR: 'toml' library is not installed. Please run 'pip install toml'")
    exit()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMPONENT_BASE_DIRS = ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers', 'formatters']

def get_global_dependencies():
    """Reads pyproject.toml to get a list of global dependencies and their versions."""
    pyproject_path = os.path.join(PROJECT_ROOT, 'pyproject.toml')
    if not os.path.exists(pyproject_path):
        print("[ERROR] pyproject.toml not found!")
        return {}, {}

    print("[INFO] Reading global dependencies from pyproject.toml...")
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        data = toml.load(f)

    deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})

    # Extract package name and the full version string
    dep_map = {}
    for pkg, version_info in deps.items():
        if pkg.lower() == 'python':
            continue
        if isinstance(version_info, dict):
            dep_map[pkg] = f"{pkg}{version_info.get('version', '*')}"
        else:
            dep_map[pkg] = f"{pkg}{version_info}"

    # Create a mapping from import name to package name (e.g., 'PIL' -> 'pillow')
    # This is a simplified version; a real-world one might need a larger map.
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
        "pandas": "pandas"
    }

    print(f"[SUCCESS] Found {len(dep_map)} global packages.")
    return dep_map, import_to_package_map

def find_imports_in_file(file_path):
    """Parses a Python file and returns a set of imported modules."""
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
    except Exception:
        # Ignore files that can't be parsed (e.g., syntax errors)
        pass
    return imports

def main():
    print("--- Starting Dependency Audit & Auto-Fix Script ---")
    global_deps, import_map = get_global_dependencies()

    fixed_components = 0

    for base_dir in COMPONENT_BASE_DIRS:
        full_base_path = os.path.join(PROJECT_ROOT, base_dir)
        if not os.path.isdir(full_base_path):
            continue

        print(f"\n--- Scanning Directory: '{base_dir}' ---")
        for component_name in os.listdir(full_base_path):
            component_path = os.path.join(full_base_path, component_name)
            if not os.path.isdir(component_path) or component_name == '__pycache__':
                continue

            requirements_path = os.path.join(component_path, 'requirements.txt')
            if os.path.exists(requirements_path):
                continue # Skip components that already have their dependencies defined

            found_deps_for_component = set()

            for root, _, files in os.walk(component_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        imports = find_imports_in_file(file_path)
                        for imp in imports:
                            # Map import name back to package name if needed
                            package_name = import_map.get(imp, imp)
                            if package_name in global_deps:
                                found_deps_for_component.add(package_name)

            if found_deps_for_component:
                print(f"[FIXING] -> Component '{component_name}' has undeclared dependencies.")
                fixed_components += 1
                try:
                    with open(requirements_path, 'w', encoding='utf-8') as f:
                        for dep_name in sorted(list(found_deps_for_component)):
                            full_dep_string = global_deps[dep_name]
                            f.write(f"{full_dep_string}\n")
                            print(f"    -> Added '{full_dep_string}' to its new requirements.txt")
                    print(f"[SUCCESS] -> Created and populated requirements.txt for '{component_name}'.")
                except IOError as e:
                    print(f"[ERROR] -> Could not write requirements.txt for '{component_name}': {e}")

    print("\n--- Audit Complete ---")
    if fixed_components > 0:
        print(f"[SUCCESS] {fixed_components} components were auto-fixed with a new 'requirements.txt'.")
        print("You can now restart Flowork. It will automatically install these local dependencies.")
    else:
        print("[SUCCESS] All components that need dependencies already have a requirements.txt. No fixes were needed.")
        print("You are one step closer to removing the 'libs' folder!")

if __name__ == "__main__":
    main()