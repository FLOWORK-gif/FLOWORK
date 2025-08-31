#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\generate_docs.py
# JUMLAH BARIS : 244
#######################################################################

import os
import json
import shutil
import re
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGUAGES = ['id', 'en']
DEFAULT_LANG = 'en'
COMPONENT_DIRS = ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers']
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
def ensure_packages_are_importable():
    print("[INFO] Ensuring component directories are importable...")
    for comp_dir in COMPONENT_DIRS:
        init_path = os.path.join(PROJECT_ROOT, comp_dir, '__init__.py')
        if not os.path.exists(init_path):
            try:
                with open(init_path, 'w') as f:
                    pass
                print(f"  -> Created: {os.path.relpath(init_path, PROJECT_ROOT)}")
            except Exception as e:
                print(f"  [WARNING] Could not create __init__.py in '{comp_dir}': {e}")
        full_comp_dir_path = os.path.join(PROJECT_ROOT, comp_dir)
        if os.path.isdir(full_comp_dir_path):
            for item_name in os.listdir(full_comp_dir_path):
                item_path = os.path.join(full_comp_dir_path, item_name)
                if os.path.isdir(item_path):
                    sub_init_path = os.path.join(item_path, '__init__.py')
                    if not os.path.exists(sub_init_path):
                        try:
                            with open(sub_init_path, 'w') as f:
                                pass
                        except Exception as e:
                            print(f"  [WARNING] Could not create __init__.py in '{item_path}': {e}")
def load_translations(lang_code: str) -> dict:
    translations = {}
    for dir_path, _, filenames in os.walk(PROJECT_ROOT):
        if 'locales' in dir_path:
            lang_file = os.path.join(dir_path, f"{lang_code}.json")
            if os.path.exists(lang_file):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        translations.update(json.load(f))
                except json.JSONDecodeError:
                    print(f"[WARNING] Could not parse JSON from: {lang_file}")
    return translations
def _generate_markdown_table(headers, rows):
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = []
    for row in rows:
        cleaned_row = [str(cell).replace('|', '\\|').replace('\n', '<br>') for cell in row]
        row_lines.append("| " + " | ".join(cleaned_row) + " |")
    return "\n".join([header_line, separator_line] + row_lines)
def generate_component_doc(component_dir: str, component_id: str, manifest: dict, lang: str, translations: dict) -> dict:
    name = translations.get(manifest.get('name_key'), manifest.get('name', component_id))
    description = translations.get(manifest.get('description_key'), manifest.get('description', ''))
    tutorial = translations.get(manifest.get('tutorial_key'), '')
    entry_point = manifest.get('entry_point', '')
    tier = manifest.get('tier', 'free').capitalize()
    version = manifest.get('version', '1.0')
    author = manifest.get('author', 'N/A')
    md_content = f"# {name}\n\n"
    md_content += f"> {description}\n\n"
    meta_headers = ["Attribute", "Value"]
    meta_rows = [
        ["ID", f"`{component_id}`"],
        ["Tier", tier],
        ["Version", version],
        ["Author", author]
    ]
    md_content += "## Metadata\n\n"
    md_content += _generate_markdown_table(meta_headers, meta_rows) + "\n\n"
    if tutorial:
        md_content += f"## How to Use\n{tutorial}\n\n"
    properties = manifest.get('properties', [])
    if properties:
        prop_headers = ["ID (`config`)", "Label", "Type", "Default Value"]
        prop_rows = []
        for prop in properties:
            prop_id = prop.get('id', 'N/A')
            prop_label_key = prop.get('label', '')
            prop_label = translations.get(prop_label_key, prop_label_key)
            prop_type = prop.get('type', 'string')
            prop_default = prop.get('default', '')
            prop_rows.append([f"`{prop_id}`", prop_label, f"`{prop_type}`", f"`{prop_default}`"])
        md_content += "## Configuration Properties\n\n"
        md_content += _generate_markdown_table(prop_headers, prop_rows) + "\n\n"
    output_ports = manifest.get('output_ports', [])
    if output_ports:
        port_headers = ["Port Name", "Display Name"]
        port_rows = []
        for port in output_ports:
            port_name = port.get('name', 'N/A')
            port_display_key = port.get('display_name', '')
            port_display = translations.get(port_display_key, port_display_key)
            port_rows.append([f"`{port_name}`", port_display])
        md_content += "## Output Ports\n\n"
        md_content += _generate_markdown_table(port_headers, port_rows) + "\n\n"
    output_schema = manifest.get('output_schema', [])
    if output_schema:
        if isinstance(output_schema, list) and all(isinstance(item, dict) for item in output_schema):
            schema_headers = ["Payload Path (`data.key`)", "Data Type", "Description"]
            schema_rows = []
            for schema in output_schema:
                schema_name = schema.get('name', 'N/A')
                schema_type = schema.get('type', 'any')
                schema_desc = schema.get('description', '')
                schema_rows.append([f"`{schema_name}`", f"`{schema_type}`", schema_desc])
            md_content += "## Output Data Schema\n\nThis module adds the following keys to `payload['data']`:\n\n"
            md_content += _generate_markdown_table(schema_headers, schema_rows) + "\n\n"
        else:
            md_content += "## Output Data Schema\n\nThis module has a non-standard output schema:\n\n"
            md_content += f"```json\n{json.dumps(output_schema, indent=2)}\n```\n\n"
    python_path_for_docstring = ""
    if entry_point:
        processor_module_path = entry_point.split('.')[0]
        python_path_for_docstring = f"{component_dir}.{component_id}.{processor_module_path}"
        md_content += f"## API Reference\n\n::: {python_path_for_docstring}\n"
    lang_path_segment = "" if lang == DEFAULT_LANG else lang
    doc_filename = f"{component_id}.md"
    output_path = os.path.join(DOCS_DIR, lang_path_segment, 'reference', component_dir, doc_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    nav_path = os.path.join('reference', component_dir, doc_filename).replace('\\', '/')
    return {name: nav_path}
def main():
    print("[INFO] Starting automatic documentation generation...")
    ensure_packages_are_importable()
    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
    os.makedirs(DOCS_DIR)
    print(f"[INFO] Cleaned up and recreated docs directory at: {DOCS_DIR}")
    nav_paths = {comp_dir: [] for comp_dir in COMPONENT_DIRS}
    for lang in LANGUAGES:
        print(f"--- Generating for language: '{lang}' ---")
        translations = load_translations(lang)
        lang_path_segment = "" if lang == DEFAULT_LANG else lang
        lang_dir = os.path.join(DOCS_DIR, lang_path_segment)
        os.makedirs(lang_dir, exist_ok=True)
        guides_dir = os.path.join(lang_dir, 'guides')
        os.makedirs(guides_dir, exist_ok=True)
        with open(os.path.join(lang_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(f'# {translations.get("doc_homepage_title", "Flowork Documentation")}')
        for comp_dir in COMPONENT_DIRS:
            full_path = os.path.join(PROJECT_ROOT, comp_dir)
            if not os.path.isdir(full_path):
                continue
            for component_id in sorted(os.listdir(full_path)):
                component_path = os.path.join(full_path, component_id)
                if os.path.isdir(component_path) and component_id != '__pycache__':
                    manifest_path = os.path.join(component_path, 'manifest.json')
                    if os.path.exists(manifest_path):
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        nav_entry = generate_component_doc(comp_dir, component_id, manifest, lang, translations)
                        if lang == DEFAULT_LANG:
                            nav_paths[comp_dir].append(nav_entry)
    print("--- Generating mkdocs.yml configuration ---")
    config_lines = [
        "# This file is auto-generated by scripts/generate_docs.py",
        "# Do not edit manually.",
        "",
        "site_name: Flowork - Documentation",
        "site_url: https://www.teetah.art/flowork/docs/",
        "repo_url: https://github.com/FLOWORK-gif/FLOWORK",
        "repo_name: FLOWORK-gif/FLOWORK",
        "",
        "theme:",
        f"  name: material",
        f"  language: {DEFAULT_LANG}",
        "  features:",
        "    - navigation.tabs",
        "    - navigation.sections",
        "    - content.code.copy",
        "    - search.suggest",
        "  palette:",
        "    scheme: slate",
        "    primary: indigo",
        "    accent: blue",
        "",
        "extra:",
        "  alternate:"
    ]
    for lang in LANGUAGES:
        lang_name = "Bahasa Indonesia" if lang == "id" else "English"
        link = f"./{lang}/"
        config_lines.append(f"    - name: {lang_name}")
        config_lines.append(f"      link: {link}")
        config_lines.append(f"      lang: {lang}")
    config_lines.append("")
    config_lines.append("nav:")
    config_lines.append("  - Home: index.md")
    config_lines.append("  - API Guides:")
    config_lines.append("    - Introduction: guides/introduction.md")
    config_lines.append("    - Getting Started: guides/getting-started.md")
    config_lines.append("    - Authentication: guides/authentication.md")
    config_lines.append("    - Practical Scenarios: guides/scenarios.md")
    config_lines.append("    - Best Practices: guides/best-practices.md")
    config_lines.append("  - Component Reference:")
    config_lines.append("    - Introduction: reference/index.md")
    for comp_dir, nav_entries in nav_paths.items():
        if nav_entries:
            dir_name_pretty = comp_dir.replace('_', ' ').title()
            config_lines.append(f"    - {dir_name_pretty}:")
            for entry in sorted(nav_entries, key=lambda x: list(x.keys())[0]):
                for name, path in entry.items():
                    safe_name = name.replace("'", "''")
                    config_lines.append(f"      - '{safe_name}': {path}")
    config_lines.extend([
        "",
        "plugins:",
        "  - search",
        "  - mkdocstrings:",
        "      handlers:",
        "        python:",
        "          options:",
        "            show_source: false",
        "            docstring_style: google",
        "            show_root_heading: true",
        "            members_order: source",
        "            # [PERBAIKAN] Memindahkan 'paths' ke dalam 'extra' untuk mengikuti standar baru",
        "            extra:",
        "              paths: [., modules, plugins, widgets, triggers, ai_providers]"
    ])
    mkdocs_config = "\n".join(config_lines)
    with open(os.path.join(PROJECT_ROOT, 'mkdocs.yml'), 'w', encoding='utf-8') as f:
        f.write(mkdocs_config)
    for lang in LANGUAGES:
        lang_path_segment = "" if lang == DEFAULT_LANG else lang
        ref_index_path = os.path.join(DOCS_DIR, lang_path_segment, 'reference', 'index.md')
        os.makedirs(os.path.dirname(ref_index_path), exist_ok=True)
        with open(ref_index_path, 'w', encoding='utf-8') as f:
            f.write("# Component Reference\n\nThis section provides a detailed, auto-generated reference for every component available in Flowork.")
    print("\n[SUCCESS] Documentation generation complete!")
    print("To view your documentation, run 'poetry run mkdocs serve' in your terminal.")
if __name__ == "__main__":
    main()
