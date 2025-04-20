from django.core.management.base import BaseCommand
from django.db import connection, transaction
import datetime

class Command(BaseCommand):
    help = 'Sets up the database schema for the education app'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database schema...')
        
        # Check if the education_user table exists
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='education_user'"
            )
            if cursor.fetchone():
                self.stdout.write(self.style.SUCCESS('education_user table already exists.'))
            else:
                self.create_tables()
        
        # Check if the migration record exists
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM django_migrations WHERE app='education' AND name='0001_initial'"
            )
            if cursor.fetchone():
                self.stdout.write(self.style.SUCCESS('Migration record already exists.'))
            else:
                self.create_migration_record()
        
        self.stdout.write(self.style.SUCCESS('Database setup completed!'))
    
    def create_tables(self):
        self.stdout.write('Creating tables...')
        
        # SQL statements to create tables
        tables = [
            """
            CREATE TABLE education_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password VARCHAR(128) NOT NULL,
                last_login DATETIME NULL,
                is_superuser BOOLEAN NOT NULL,
                username VARCHAR(150) NOT NULL UNIQUE,
                first_name VARCHAR(150) NOT NULL,
                last_name VARCHAR(150) NOT NULL,
                email VARCHAR(254) NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined DATETIME NOT NULL,
                role VARCHAR(10) NOT NULL,
                bio TEXT NOT NULL,
                avatar VARCHAR(100) NULL,
                email_notifications BOOLEAN NOT NULL,
                push_notifications BOOLEAN NOT NULL
            );
            """,
            """
            CREATE TABLE education_user_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES education_user (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES auth_group (id) ON DELETE CASCADE,
                UNIQUE (user_id, group_id)
            );
            """,
            """
            CREATE TABLE education_user_user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES education_user (id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES auth_permission (id) ON DELETE CASCADE,
                UNIQUE (user_id, permission_id)
            );
            """,
            """
            CREATE TABLE education_course (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                thumbnail VARCHAR(100) NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                category VARCHAR(50) NOT NULL,
                difficulty VARCHAR(20) NOT NULL,
                instructor_id INTEGER NOT NULL,
                FOREIGN KEY (instructor_id) REFERENCES education_user (id)
            );
            """,
            """
            CREATE TABLE education_course_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (course_id) REFERENCES education_course (id),
                FOREIGN KEY (user_id) REFERENCES education_user (id),
                UNIQUE (course_id, user_id)
            );
            """
        ]
        
        with connection.cursor() as cursor:
            for sql in tables:
                cursor.execute(sql)
            connection.commit()
        
        self.stdout.write(self.style.SUCCESS('Tables created!'))
    
    def create_migration_record(self):
        self.stdout.write('Creating migration record...')
        
        # Get the current timestamp
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        with connection.cursor() as cursor:
            # Make sure the django_migrations table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'"
            )
            if not cursor.fetchone():
                cursor.execute(
                    "CREATE TABLE django_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "app VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, applied DATETIME NOT NULL)"
                )
            
            # Insert the migration record
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
                ['education', '0001_initial', now]
            )
            connection.commit()
        
        self.stdout.write(self.style.SUCCESS('Migration record created!')) 