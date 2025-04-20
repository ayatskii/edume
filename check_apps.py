import os
import sys
import importlib
import inspect

# Output file
output_file = "app_check_output.txt"
with open(output_file, "w") as f:
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_system.settings')
    import django
    django.setup()

    # Import necessary components
    from django.apps import apps
    from django.conf import settings
    from django.db.migrations.loader import MigrationLoader

    f.write(f"Current working directory: {os.getcwd()}\n")

    # Check installed apps
    f.write("\nINSTALLED_APPS in settings.py:\n")
    for app in settings.INSTALLED_APPS:
        f.write(f" - {app}\n")

    f.write("\nApps registered with Django:\n")
    for app_config in apps.get_app_configs():
        f.write(f" - {app_config.name} (label: {app_config.label}, path: {app_config.path})\n")

    # Check migration loader
    f.write("\nMigration Loader information:\n")
    loader = MigrationLoader(None)
    f.write(f"Disk migrations: {list(loader.disk_migrations.keys())}\n")
    f.write(f"Graph nodes: {list(loader.graph.nodes.keys())}\n")

    f.write("\nDetailed check of the education app:\n")
    try:
        education_module = importlib.import_module('education')
        f.write(f"Module location: {inspect.getfile(education_module)}\n")
        f.write(f"Module path: {education_module.__path__}\n")
        
        # Check if migrations can be imported
        try:
            migrations_module = importlib.import_module('education.migrations')
            f.write(f"Migrations module location: {inspect.getfile(migrations_module)}\n")
            f.write(f"Migrations module path: {migrations_module.__path__}\n")
            
            # Try to import the initial migration
            try:
                initial_migration = importlib.import_module('education.migrations.0001_initial')
                f.write(f"Initial migration module found at: {inspect.getfile(initial_migration)}\n")
                f.write(f"Migration class: {initial_migration.Migration}\n")
            except ImportError as e:
                f.write(f"Failed to import initial migration: {e}\n")
        except ImportError as e:
            f.write(f"Failed to import migrations module: {e}\n")
    except ImportError as e:
        f.write(f"Failed to import education module: {e}\n")

    # Check Python path
    f.write("\nPython path:\n")
    for path in sys.path:
        f.write(f" - {path}\n")

print(f"Diagnostic information written to {output_file}") 