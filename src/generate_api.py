# scripts/generate_api.py
import importlib
import inspect
from pathlib import Path
import yaml

MODULES_DIR = Path("src/biopap/modules")
DOCS_API_DIR = Path("docs/api")
MKDOCS_FILE = Path("mkdocs.yml")

# Ensure docs/api exists
DOCS_API_DIR.mkdir(parents=True, exist_ok=True)

# Prepare nav entries
nav_modules = []

# Scan all .py files in modules folder
for file in MODULES_DIR.glob("*.py"):
    if file.name in ("__init__.py", "base_class.py"):
        continue

    module_name = file.stem  # e.g., anonymize

    # Import module dynamically
    mod = importlib.import_module(f"biopap.modules.{module_name}")

    # Get classes defined in this module (exclude BaseClass)
    classes = [
        cls for name, cls in inspect.getmembers(mod, inspect.isclass)
        if cls.__module__ == mod.__name__ and name.lower() != "baseclass"
    ]

    if len(classes) != 1:
        print((f"warning: Module {module_name} has {len(classes)} non-base classes, skipped"))
        continue

    class_name = classes[0].__name__

    # Write Markdown for the module
    md_path = DOCS_API_DIR / f"{module_name}.md"
    with open(md_path, "w") as f:
        f.write(f"# {class_name}\n\n::: biopap.modules.{module_name}.{class_name}\n")

    print(f"Generated {md_path} for class {class_name}")

    # Add to nav
    nav_modules.append({class_name: f"api/{module_name}.md"})

# Update mkdocs.yml nav
with open(MKDOCS_FILE, "r") as f:
    mkdocs_data = yaml.safe_load(f)

nav = mkdocs_data.get("nav", [])
nav = [item for item in nav if "Modules" not in item]

nav.append({"Modules": nav_modules})
mkdocs_data["nav"] = nav

with open(MKDOCS_FILE, "w") as f:
    yaml.dump(mkdocs_data, f, sort_keys=False)

print("Updated mkdocs.yml nav with modules")