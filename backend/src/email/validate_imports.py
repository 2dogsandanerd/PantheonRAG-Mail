import ast
import os
import sys
from pathlib import Path

def validate_module_imports():
    """Validate that all imports in email modules are clean"""
    print("🔍 VALIDATING EMAIL MODULE IMPORTS")
    print("=" * 45)

    email_dir = Path("src/email")
    issues = []

    for py_file in email_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        print(f"📄 Checking {py_file}...")

        try:
            with open(py_file, 'r') as f:
                content = f.read()

            tree = ast.parse(content)

            # Check for imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check for potentially problematic imports
                        if any(bad in alias.name for bad in ['mock', 'fake', 'test']):
                            if not str(py_file).endswith('test.py'):
                                issues.append(f"{py_file}: Suspicious import {alias.name}")

                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(bad in node.module for bad in ['mock', 'fake', 'test']):
                        if not str(py_file).endswith('test.py'):
                            issues.append(f"{py_file}: Suspicious import from {node.module}")

        except Exception as e:
            issues.append(f"{py_file}: Parse error - {e}")

    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ All imports look clean")

    return len(issues) == 0

def check_circular_imports():
    """Check for circular import patterns"""
    print("\n🔄 CHECKING FOR CIRCULAR IMPORTS")
    print("=" * 35)

    # Simple check - look for relative imports that could cause cycles
    email_dir = Path("src/email")
    potential_cycles = []

    for py_file in email_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                if "from .." in line and "import" in line:
                    # Check if it's importing from a peer module
                    if any(peer in line for peer in ['clients', 'core', 'unified', 'providers', 'utils']):
                        potential_cycles.append(f"{py_file}:{i} - {line.strip()}")

        except Exception as e:
            print(f"   Error reading {py_file}: {e}")

    if potential_cycles:
        print("\n⚠️  POTENTIAL CIRCULAR IMPORTS:")
        for cycle in potential_cycles:
            print(f"   {cycle}")
    else:
        print("\n✅ No obvious circular import patterns")

    return len(potential_cycles) == 0

def check_unused_imports():
    """Check for potentially unused imports"""
    print("\n🗂️  CHECKING FOR UNUSED IMPORTS")
    print("=" * 35)

    email_dir = Path("src/email")
    unused_imports = []

    for py_file in email_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or str(py_file).endswith('__init__.py'):
            continue

        try:
            with open(py_file, 'r') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []
            names_used = set()

            # Collect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.asname if alias.asname else alias.name
                        imports.append((import_name, alias.name))

                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        import_name = alias.asname if alias.asname else alias.name
                        imports.append((import_name, f"{node.module}.{alias.name}"))

                # Collect used names
                elif isinstance(node, ast.Name):
                    names_used.add(node.id)

            # Check for unused imports
            for import_alias, import_full in imports:
                if import_alias not in names_used and not import_alias.startswith('_'):
                    unused_imports.append(f"{py_file}: Potentially unused import '{import_alias}' ({import_full})")

        except Exception as e:
            print(f"   Error analyzing {py_file}: {e}")

    if unused_imports:
        print("\n⚠️  POTENTIALLY UNUSED IMPORTS:")
        for unused in unused_imports[:10]:  # Limit to first 10
            print(f"   {unused}")
        if len(unused_imports) > 10:
            print(f"   ... and {len(unused_imports) - 10} more")
    else:
        print("\n✅ No obviously unused imports found")

    return len(unused_imports) == 0

if __name__ == "__main__":
    imports_clean = validate_module_imports()
    no_cycles = check_circular_imports()
    no_unused = check_unused_imports()
    production_deps_ok = test_production_dependencies()

    print(f"\n📊 IMPORT VALIDATION SUMMARY")
    print("=" * 40)
    print(f"✅ Clean imports: {imports_clean}")
    print(f"✅ No circular imports: {no_cycles}")
    print(f"✅ No unused imports: {no_unused}")
    print(f"✅ Production dependencies: {production_deps_ok}")

    # Exit with error code if issues found
    if not (imports_clean and no_cycles and no_unused and production_deps_ok):
        sys.exit(1)

def test_production_dependencies():
    """Test that all production dependencies are available"""
    print("\n📦 PRODUCTION DEPENDENCY TEST")
    print("=" * 35)

    production_deps = [
        ("google.auth", "Google authentication"),
        ("google.oauth2", "Google OAuth2"),
        ("googleapiclient", "Google API client"),
        ("loguru", "Logging framework"),
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("httpx", "HTTP client for testing"),
    ]

    missing_deps = []

    for dep_name, description in production_deps:
        try:
            __import__(dep_name)
            print(f"✅ {dep_name}: {description}")
        except ImportError:
            print(f"❌ {dep_name}: Missing - {description}")
            missing_deps.append(dep_name)

    if missing_deps:
        print(f"\n⚠️  Install missing dependencies:")
        print(f"pip install {' '.join(missing_deps)}")
        return False

    return True
