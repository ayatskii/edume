import os
import django
import datetime
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education_system.settings')
django.setup()

# Add a record for the education migration
with connection.cursor() as cursor:
    # Check if the migration is already in the table
    cursor.execute(
        "SELECT id FROM django_migrations WHERE app='education' AND name='0001_initial'"
    )
    if cursor.fetchone():
        print("Migration already exists in the database.")
    else:
        # Get the current timestamp in the format Django uses
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        # Insert the migration record
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            ['education', '0001_initial', now]
        )
        connection.commit()
        print("Manually added education.0001_initial to the migrations table.")

# Check all migrations in the table
with connection.cursor() as cursor:
    cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY app, name")
    print("\nMigrations in the database:")
    for row in cursor.fetchall():
        print(f" - {row[0]}.{row[1]} (applied: {row[2]})") 