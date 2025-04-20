import os
import importlib
import re
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_system.settings')
django.setup()

# Path to education initial migration
migration_path = 'education/migrations/0001_initial.py'

# Read the file content
with open(migration_path, 'r') as f:
    content = f.read()

# Modify the dependencies to include admin.0001_initial
# This avoids the circular dependency issue
new_content = re.sub(
    r"dependencies = \[\s*\('auth', '0012_alter_user_first_name_max_length'\),\s*\]",
    "dependencies = [\n        ('auth', '0012_alter_user_first_name_max_length'),\n        ('admin', '0001_initial'),\n    ]",
    content
)

# Write back to the file
with open(migration_path, 'w') as f:
    f.write(new_content)

print(f"Updated dependencies in {migration_path}")

# Try to reload the migration module
try:
    module_path = 'education.migrations.0001_initial'
    
    # Force reload if it's already loaded
    if module_path in sys.modules:
        del sys.modules[module_path]
    
    # Reload the module
    module = importlib.import_module(module_path)
    
    print(f"Successfully reloaded the migration module.")
    print(f"New dependencies: {module.Migration.dependencies}")
except Exception as e:
    print(f"Error reloading migration module: {e}") 