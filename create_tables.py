import os
import sqlite3
import datetime

# Database path
db_path = 'db.sqlite3'

# SQL statements to create tables
tables = [
    """
    CREATE TABLE IF NOT EXISTS education_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password VARCHAR(128) NOT NULL,
        last_login DATETIME NULL,
        is_superuser BOOLEAN NOT NULL DEFAULT 0,
        username VARCHAR(150) NOT NULL UNIQUE,
        first_name VARCHAR(150) NOT NULL DEFAULT '',
        last_name VARCHAR(150) NOT NULL DEFAULT '',
        email VARCHAR(254) NOT NULL DEFAULT '',
        is_staff BOOLEAN NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        date_joined DATETIME NOT NULL,
        role VARCHAR(10) NOT NULL DEFAULT 'student',
        bio TEXT NOT NULL DEFAULT '',
        avatar VARCHAR(100) NULL,
        email_notifications BOOLEAN NOT NULL DEFAULT 1,
        push_notifications BOOLEAN NOT NULL DEFAULT 1
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_user_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES education_user (id) ON DELETE CASCADE,
        FOREIGN KEY (group_id) REFERENCES auth_group (id) ON DELETE CASCADE,
        UNIQUE (user_id, group_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_user_user_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES education_user (id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id) ON DELETE CASCADE,
        UNIQUE (user_id, permission_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_course (
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
    CREATE TABLE IF NOT EXISTS education_course_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES education_course (id),
        FOREIGN KEY (user_id) REFERENCES education_user (id),
        UNIQUE (course_id, user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_module (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        "order" INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES education_course (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_lesson (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        content TEXT NOT NULL,
        video_url VARCHAR(200) NOT NULL,
        "order" INTEGER NOT NULL,
        duration VARCHAR(200) NOT NULL,
        module_id INTEGER NOT NULL,
        FOREIGN KEY (module_id) REFERENCES education_module (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_lessonprogress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        completed BOOLEAN NOT NULL,
        completed_at DATETIME NULL,
        score INTEGER NULL,
        lesson_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (lesson_id) REFERENCES education_lesson (id),
        FOREIGN KEY (user_id) REFERENCES education_user (id),
        UNIQUE (user_id, lesson_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_exam (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        duration VARCHAR(200) NOT NULL,
        due_date DATETIME NOT NULL,
        total_marks INTEGER NOT NULL,
        passing_marks INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES education_course (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_question (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_type VARCHAR(10) NOT NULL,
        text TEXT NOT NULL,
        marks INTEGER NOT NULL,
        "order" INTEGER NOT NULL,
        exam_id INTEGER NOT NULL,
        FOREIGN KEY (exam_id) REFERENCES education_exam (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_choice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text VARCHAR(200) NOT NULL,
        is_correct BOOLEAN NOT NULL,
        question_id INTEGER NOT NULL,
        FOREIGN KEY (question_id) REFERENCES education_question (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_examsubmission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitted_at DATETIME NOT NULL,
        score INTEGER NULL,
        is_passed BOOLEAN NOT NULL,
        exam_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (exam_id) REFERENCES education_exam (id),
        FOREIGN KEY (user_id) REFERENCES education_user (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_answer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_answer TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        submission_id INTEGER NOT NULL,
        FOREIGN KEY (question_id) REFERENCES education_question (id),
        FOREIGN KEY (submission_id) REFERENCES education_examsubmission (id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS education_answer_selected_choices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer_id INTEGER NOT NULL,
        choice_id INTEGER NOT NULL,
        FOREIGN KEY (answer_id) REFERENCES education_answer (id),
        FOREIGN KEY (choice_id) REFERENCES education_choice (id),
        UNIQUE (answer_id, choice_id)
    );
    """
]

# Create tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for sql in tables:
    try:
        cursor.execute(sql)
        print(f"Successfully executed: {sql[:50]}...")
    except Exception as e:
        print(f"Error executing: {sql[:50]}... - Error: {e}")

# Add migration record
migration_record_sql = """
INSERT INTO django_migrations (app, name, applied)
VALUES (?, ?, ?)
"""

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

try:
    cursor.execute(
        "SELECT id FROM django_migrations WHERE app='education' AND name='0001_initial'"
    )
    if cursor.fetchone():
        print("Migration record already exists.")
    else:
        cursor.execute(migration_record_sql, ('education', '0001_initial', now))
        print("Added migration record for education.0001_initial")
except Exception as e:
    print(f"Error adding migration record: {e}")

# Create a superuser
admin_sql = """
INSERT INTO education_user (
    password, is_superuser, username, first_name, last_name,
    email, is_staff, is_active, date_joined, role
)
VALUES (
    'pbkdf2_sha256$720000$afz0Q21s9l3Fl7M8QQ18z6$o46AXSYDVdO8gH9GvPR1V7hhqqUxO02Kd7XWkF+eJR0=',  -- Password: admin
    1, 'admin', 'Admin', 'User',
    'admin@example.com', 1, 1, ?, 'admin'
)
"""

try:
    cursor.execute(
        "SELECT id FROM education_user WHERE username='admin'"
    )
    if cursor.fetchone():
        print("Admin user already exists.")
    else:
        cursor.execute(admin_sql, (now,))
        print("Created admin user (username: admin, password: admin)")
except Exception as e:
    print(f"Error creating admin user: {e}")

conn.commit()
conn.close()

print("\nDatabase setup completed!") 