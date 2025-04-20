import random
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
from django.conf import settings
from education.models import User, Course, Module, Lesson
import os
import datetime

class Command(BaseCommand):
    help = 'Populates the database with placeholder courses'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Number of courses to create')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} placeholder courses...')

        # Ensure we have at least one teacher
        try:
            teacher = User.objects.filter(role='teacher').first()
            if not teacher:
                teacher_username = 'teacher'
                teacher_email = 'teacher@example.com'
                teacher = User.objects.create_user(
                    username=teacher_username,
                    email=teacher_email,
                    password='password123',
                    role='teacher',
                    first_name='Test',
                    last_name='Teacher',
                )
                self.stdout.write(self.style.SUCCESS(f'Created teacher user: {teacher_username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating teacher: {str(e)}'))
            return

        # Course categories and difficulties
        categories = ['Programming', 'Data Science', 'Web Development', 'Mobile Development', 
                      'DevOps', 'Design', 'Business', 'Marketing', 'Language Learning', 'Mathematics']
        
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        # Sample course titles and descriptions
        course_prefixes = ['Introduction to', 'Advanced', 'Mastering', 'Fundamentals of', 
                           'Complete Guide to', 'The Art of', 'Professional', 'Ultimate', 
                           'Practical', 'Essential']
        
        # Create courses
        for i in range(count):
            try:
                category = random.choice(categories)
                title = f"{random.choice(course_prefixes)} {category} {i+1}"
                description = f"This is a placeholder course for {category}. Learn everything you need to know about this subject in a comprehensive and structured way. This course includes practical exercises and real-world examples."
                
                # Create course
                course = Course.objects.create(
                    title=title,
                    description=description,
                    # No actual file upload for simplicity
                    thumbnail='course_thumbnails/placeholder.jpg',
                    instructor=teacher,
                    category=category,
                    difficulty=random.choice(difficulties)
                )
                
                # Create 3-5 modules per course
                module_count = random.randint(3, 5)
                for j in range(module_count):
                    module = Module.objects.create(
                        course=course,
                        title=f"Module {j+1}: {random.choice(['Introduction', 'Fundamentals', 'Advanced Topics', 'Practical Applications', 'Case Studies'])}",
                        description=f"This module covers key concepts related to {category} with practical examples and exercises.",
                        order=j+1
                    )
                    
                    # Create 3-7 lessons per module
                    lesson_count = random.randint(3, 7)
                    for k in range(lesson_count):
                        Lesson.objects.create(
                            module=module,
                            title=f"Lesson {k+1}: {random.choice(['Getting Started', 'Key Concepts', 'Practical Example', 'Deep Dive', 'Case Study', 'Best Practices', 'Advanced Techniques'])}",
                            content=f"This is placeholder content for Lesson {k+1} in Module {j+1} of the {title} course.",
                            video_url=f"https://example.com/videos/{slugify(title)}-module-{j+1}-lesson-{k+1}",
                            order=k+1,
                            duration=datetime.timedelta(minutes=random.randint(10, 60))
                        )
                
                self.stdout.write(self.style.SUCCESS(f'Created course: {title} with {module_count} modules'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating course {i+1}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} placeholder courses')) 