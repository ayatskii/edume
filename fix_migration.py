import os
import sys
import django
from django.core.management import call_command
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_system.settings')
django.setup()

# First, manually create the migrations table if it doesn't exist
with connection.cursor() as cursor:
    # Check if django_migrations table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'"
    )
    if not cursor.fetchone():
        print("Creating django_migrations table...")
        cursor.execute(
            "CREATE TABLE django_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "app VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, applied DATETIME NOT NULL)"
        )
        connection.commit()

# Try to apply migrations for all apps
print("Applying migrations...")
try:
    call_command('migrate', verbosity=2)
except Exception as e:
    print(f"Error during migration: {e}")

# Try to fake the initial migration for education app
print("\nTrying to fake initial migration for education app...")
try:
    call_command('migrate', 'education', '0001_initial', fake=True, verbosity=2)
except Exception as e:
    print(f"Error during fake migration: {e}")

# Check the migration status
print("\nChecking migration status...")
try:
    call_command('showmigrations', verbosity=2)
except Exception as e:
    print(f"Error showing migrations: {e}") 