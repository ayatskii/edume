# Education System

This is a Django-based education system with courses, lessons, exams, and user management.

## Setup

1. The database tables have been created manually due to migration issues.
2. An admin user has been created with:
   - Username: `admin`
   - Password: `admin`

## Current Status

The system has the following components:

- Core models (User, Course, Module, Lesson, Exam, etc.)
- Templates for various pages
- Basic URL configuration

## Known Issues and Solutions

### Migration Issues

There are currently issues with Django's migration system recognizing the apps. The following workarounds have been implemented:

1. Database tables have been created directly using SQL statements.
2. A migration record has been added to the django_migrations table.

### Next Steps

To continue development:

1. **Run the server:**
   ```
   python manage.py runserver
   ```

2. **Access the admin interface:**
   - Go to http://localhost:8000/admin/
   - Log in with admin/admin

3. **To manually add data to the tables:**
   - Use the Django shell or SQL directly
   - Example using Django shell:
     ```python
     python manage.py shell
     from education.models import Course, User
     admin = User.objects.get(username='admin')
     course = Course.objects.create(
         title='Sample Course',
         description='A sample course',
         thumbnail='course_thumbnails/sample.jpg',
         instructor=admin,
         category='General',
         difficulty='beginner'
     )
     ```

4. **Further troubleshooting:**
   - Check Django version compatibility
   - Ensure all __init__.py files are present in packages
   - Review app configurations
   - Consider recreating the migrations 