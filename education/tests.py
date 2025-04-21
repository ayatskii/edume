from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Course, Module, Lesson, Exam, Question, Choice

User = get_user_model()

class PermissionTestCase(TestCase):
    """Test that only course instructors can modify their courses and content"""
    
    def setUp(self):
        # Create two teacher users
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password123',
            role='teacher'
        )
        self.other_teacher = User.objects.create_user(
            username='otherteacher',
            email='other@example.com',
            password='password123',
            role='teacher'
        )
        # Create a student user
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='password123',
            role='student'
        )
        
        # Create a course owned by the instructor
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            category='test',
            difficulty='intermediate'
        )
        
        # Create a module in the course
        self.module = Module.objects.create(
            title='Test Module',
            description='Module Description',
            course=self.course,
            order=1
        )
        
        # Create a lesson in the module
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Lesson Content',
            module=self.module,
            order=1,
            duration=timedelta(minutes=30)
        )
        
        # Create an exam in the course
        self.exam = Exam.objects.create(
            title='Test Exam',
            description='Exam Description',
            course=self.course,
            duration=timedelta(hours=1),
            due_date=timezone.now() + timedelta(days=7),
            total_marks=100,
            passing_marks=60
        )
        
        # Create a question in the exam
        self.question = Question.objects.create(
            exam=self.exam,
            question_type='mcq',
            text='Test Question',
            marks=10,
            order=1
        )
        
        # Create a client for making requests
        self.client = Client()

    def test_course_creation_permissions(self):
        """Test that any teacher can create courses, but only the instructor can modify them"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a course
        response = self.client.post(reverse('education:course_create'), {
            'title': 'New Course',
            'description': 'New Description',
            'category': 'programming',
            'difficulty': 'beginner'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should also be able to create a course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:course_create'), {
            'title': 'Another Course',
            'description': 'Another Description',
            'category': 'math',
            'difficulty': 'advanced'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Student should not be able to create a course
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:course_create'), {
            'title': 'Student Course',
            'description': 'Student Description',
            'category': 'history',
            'difficulty': 'beginner'
        })
        self.assertNotEqual(response.status_code, 302)  # Not a redirect, access denied

    def test_course_deletion_permissions(self):
        """Test that only the instructor can delete their course"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to delete their course
        response = self.client.post(reverse('education:course_delete', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create a new course for testing other scenarios
        course = Course.objects.create(
            title='Another Test Course',
            description='Another Test Description',
            instructor=self.instructor,
            category='test',
            difficulty='beginner'
        )
        
        # Other teacher should not be able to delete the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:course_delete', args=[course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to delete the course
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:course_delete', args=[course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_module_creation_permissions(self):
        """Test that only the course instructor can create modules"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a module in their course
        response = self.client.post(reverse('education:module_create', args=[self.course.id]), {
            'title': 'New Module',
            'description': 'New Module Description',
            'order': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create a module in the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:module_create', args=[self.course.id]), {
            'title': 'Another Module',
            'description': 'Another Module Description',
            'order': 3
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to create a module
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:module_create', args=[self.course.id]), {
            'title': 'Student Module',
            'description': 'Student Module Description',
            'order': 4
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_lesson_creation_permissions(self):
        """Test that only the course instructor can create lessons"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a lesson in their module
        response = self.client.post(reverse('education:lesson_create', args=[self.module.id]), {
            'title': 'New Lesson',
            'content': 'New Lesson Content',
            'order': 2,
            'duration': '00:45:00'  # 45 minutes
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create a lesson in the module
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:lesson_create', args=[self.module.id]), {
            'title': 'Another Lesson',
            'content': 'Another Lesson Content',
            'order': 3,
            'duration': '00:30:00'  # 30 minutes
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to create a lesson
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:lesson_create', args=[self.module.id]), {
            'title': 'Student Lesson',
            'content': 'Student Lesson Content',
            'order': 4,
            'duration': '00:20:00'  # 20 minutes
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_exam_creation_permissions(self):
        """Test that only the course instructor can create exams"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create an exam in their course
        response = self.client.post(reverse('education:exam_create', args=[self.course.id]), {
            'title': 'New Exam',
            'description': 'New Exam Description',
            'duration': '01:30:00',  # 1.5 hours
            'due_date': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S'),
            'total_marks': 50,
            'passing_marks': 30
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create an exam in the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:exam_create', args=[self.course.id]), {
            'title': 'Another Exam',
            'description': 'Another Exam Description',
            'duration': '01:00:00',  # 1 hour
            'due_date': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'total_marks': 40,
            'passing_marks': 24
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to create an exam
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:exam_create', args=[self.course.id]), {
            'title': 'Student Exam',
            'description': 'Student Exam Description',
            'duration': '00:45:00',  # 45 minutes
            'due_date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'total_marks': 30,
            'passing_marks': 18
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_question_creation_permissions(self):
        """Test that only the course instructor can create questions"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a question in their exam
        response = self.client.post(reverse('education:question_create', args=[self.exam.id]), {
            'question_type': 'mcq',
            'text': 'New Question',
            'marks': 5,
            'order': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create a question in the exam
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:question_create', args=[self.exam.id]), {
            'question_type': 'text',
            'text': 'Another Question',
            'marks': 10,
            'order': 3
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to create a question
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:question_create', args=[self.exam.id]), {
            'question_type': 'essay',
            'text': 'Student Question',
            'marks': 15,
            'order': 4
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_question_deletion_permissions(self):
        """Test that only the course instructor can delete questions"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to delete their question
        response = self.client.post(reverse('education:question_delete', args=[self.question.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create a new question for testing other scenarios
        question = Question.objects.create(
            exam=self.exam,
            question_type='text',
            text='Another Test Question',
            marks=5,
            order=2
        )
        
        # Other teacher should not be able to delete the question
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:question_delete', args=[question.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to delete the question
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:question_delete', args=[question.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

class CourseEnrollmentTestCase(TestCase):
    """Test course enrollment functionality"""
    
    def setUp(self):
        # Create teacher user
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password123',
            role='teacher'
        )
        # Create student users
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='password123',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='password123',
            role='student'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Enrollment Test Course',
            description='Test Description',
            instructor=self.teacher,
            category='test',
            difficulty='beginner'
        )
        
        # Create client
        self.client = Client()
    
    def test_student_can_enroll(self):
        """Test that students can enroll in courses"""
        # Login as student1
        self.client.login(username='student1', password='password123')
        
        # Student should be able to enroll in the course
        response = self.client.post(reverse('education:enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Check if student is enrolled
        self.course.refresh_from_db()
        self.assertIn(self.student1, self.course.students.all())
    
    def test_teacher_cannot_enroll(self):
        """Test that teachers cannot enroll in courses as students"""
        # Login as teacher
        self.client.login(username='teacher', password='password123')
        
        # Teacher should not be able to enroll in the course
        response = self.client.post(reverse('education:enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that teacher is not enrolled
        self.course.refresh_from_db()
        self.assertNotIn(self.teacher, self.course.students.all())

class ExamSubmissionTestCase(TestCase):
    """Test exam submission functionality"""
    
    def setUp(self):
        # Create teacher user
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='password123',
            role='teacher'
        )
        # Create student user
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='password123',
            role='student'
        )
        
        # Create a course
        self.course = Course.objects.create(
            title='Exam Test Course',
            description='Test Description',
            instructor=self.teacher,
            category='test',
            difficulty='beginner'
        )
        
        # Enroll student in course
        self.course.students.add(self.student)
        
        # Create an exam
        self.exam = Exam.objects.create(
            title='Test Exam',
            description='Exam Description',
            course=self.course,
            duration=timedelta(hours=1),
            due_date=timezone.now() + timedelta(days=7),
            total_marks=20,
            passing_marks=10
        )
        
        # Create a multiple choice question
        self.question = Question.objects.create(
            exam=self.exam,
            question_type='mcq',
            text='Test MCQ Question',
            marks=10,
            order=1
        )
        
        # Create choices for the question
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong Answer',
            is_correct=False
        )
        
        # Create a text question
        self.text_question = Question.objects.create(
            exam=self.exam,
            question_type='text',
            text='Test Text Question',
            marks=10,
            order=2
        )
        
        # Create client
        self.client = Client()
    
    def test_student_can_take_exam(self):
        """Test that enrolled students can take exams"""
        # Login as student
        self.client.login(username='student', password='password123')
        
        # Student should be able to access the exam taking page
        response = self.client.get(reverse('education:take_exam', args=[self.exam.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_teacher_cannot_take_exam(self):
        """Test that teachers cannot take exams"""
        # Login as teacher
        self.client.login(username='teacher', password='password123')
        
        # Teacher should not be able to take the exam
        response = self.client.get(reverse('education:take_exam', args=[self.exam.id]))
        self.assertNotEqual(response.status_code, 200)  # Not accessible

class CoursePermissionTests(TestCase):
    """Tests for permission controls on courses and related content"""
    
    def setUp(self):
        # Create two teacher users
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='password123',
            role='teacher'
        )
        self.other_teacher = User.objects.create_user(
            username='otherteacher',
            email='other@example.com',
            password='password123',
            role='teacher'
        )
        # Create a student user
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='password123',
            role='student'
        )
        
        # Create a course owned by the instructor
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            category='test',
            difficulty='intermediate'
        )
        
        # Create a module in the course
        self.module = Module.objects.create(
            title='Test Module',
            description='Module Description',
            course=self.course,
            order=1
        )
        
        # Create a lesson in the module
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Lesson Content',
            module=self.module,
            order=1,
            duration=timedelta(minutes=30)
        )
        
        # Create an exam in the course
        self.exam = Exam.objects.create(
            title='Test Exam',
            description='Exam Description',
            course=self.course,
            duration=timedelta(hours=1),
            due_date=timezone.now() + timedelta(days=7),
            total_marks=100,
            passing_marks=60
        )
        
        # Create a client for making requests
        self.client = Client()
    
    def test_course_deletion_permission(self):
        """Test that only the instructor can delete their course"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Create a course to delete
        course_to_delete = Course.objects.create(
            title='Course to Delete',
            description='This course will be deleted',
            instructor=self.instructor,
            category='test',
            difficulty='beginner'
        )
        
        # Instructor should be able to delete their course
        response = self.client.post(reverse('education:course_delete', args=[course_to_delete.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create another course for testing other scenarios
        other_course = Course.objects.create(
            title='Another Test Course',
            description='Another Test Description',
            instructor=self.instructor,
            category='test',
            difficulty='beginner'
        )
        
        # Other teacher should not be able to delete the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:course_delete', args=[other_course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to delete the course
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:course_delete', args=[other_course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_module_creation_permission(self):
        """Test that only the course instructor can create modules"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a module in their course
        response = self.client.post(reverse('education:module_create', args=[self.course.id]), {
            'title': 'New Module',
            'description': 'New Module Description',
            'order': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create a module in the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:module_create', args=[self.course.id]), {
            'title': 'Another Module',
            'description': 'Another Module Description',
            'order': 3
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_module_deletion_permission(self):
        """Test that only the course instructor can delete modules"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to delete their module
        response = self.client.post(reverse('education:module_delete', args=[self.module.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create a new module for testing other scenarios
        new_module = Module.objects.create(
            title='New Test Module',
            description='New Module Description',
            course=self.course,
            order=2
        )
        
        # Other teacher should not be able to delete the module
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:module_delete', args=[new_module.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_lesson_creation_permission(self):
        """Test that only the course instructor can create lessons"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create a lesson in their module
        response = self.client.post(reverse('education:lesson_create', args=[self.module.id]), {
            'title': 'New Lesson',
            'content': 'New Lesson Content',
            'order': 2,
            'duration': '00:45:00'  # 45 minutes
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create a lesson in the module
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:lesson_create', args=[self.module.id]), {
            'title': 'Another Lesson',
            'content': 'Another Lesson Content',
            'order': 3,
            'duration': '00:30:00'  # 30 minutes
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_lesson_deletion_permission(self):
        """Test that only the course instructor can delete lessons"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to delete their lesson
        response = self.client.post(reverse('education:lesson_delete', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create a new lesson for testing other scenarios
        new_lesson = Lesson.objects.create(
            title='New Test Lesson',
            content='New Lesson Content',
            module=self.module,
            order=2,
            duration=timedelta(minutes=45)
        )
        
        # Other teacher should not be able to delete the lesson
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:lesson_delete', args=[new_lesson.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_exam_creation_permission(self):
        """Test that only the course instructor can create exams"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create an exam in their course
        response = self.client.post(reverse('education:exam_create', args=[self.course.id]), {
            'title': 'New Exam',
            'description': 'New Exam Description',
            'duration': '01:30:00',  # 1.5 hours
            'due_date': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S'),
            'total_marks': 50,
            'passing_marks': 30
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create an exam in the course
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:exam_create', args=[self.course.id]), {
            'title': 'Another Exam',
            'description': 'Another Exam Description',
            'duration': '01:00:00',  # 1 hour
            'due_date': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'total_marks': 40,
            'passing_marks': 24
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_exam_deletion_permission(self):
        """Test that only the course instructor can delete exams"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to delete their exam
        response = self.client.post(reverse('education:exam_delete', args=[self.exam.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Create a new exam for testing other scenarios
        new_exam = Exam.objects.create(
            title='New Test Exam',
            description='New Exam Description',
            course=self.course,
            duration=timedelta(hours=2),
            due_date=timezone.now() + timedelta(days=14),
            total_marks=75,
            passing_marks=45
        )
        
        # Other teacher should not be able to delete the exam
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:exam_delete', args=[new_exam.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
