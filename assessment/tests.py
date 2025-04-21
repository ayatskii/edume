from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from education.models import Course, Exam, Question, Choice

User = get_user_model()

class QuestionPermissionTests(TestCase):
    """Tests for question-related permissions in the assessment app"""
    
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
        
        # Create a client for making requests
        self.client = Client()
    
    def test_question_creation_permission(self):
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
    
    def test_question_deletion_permission(self):
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
    
    def test_choice_creation_permission(self):
        """Test that only the course instructor can create choices for questions"""
        # Login as instructor
        self.client.login(username='instructor', password='password123')
        
        # Instructor should be able to create choices for their question
        response = self.client.post(reverse('education:choice_create', args=[self.question.id]), {
            'text': 'New Choice',
            'is_correct': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Other teacher should not be able to create choices
        self.client.login(username='otherteacher', password='password123')
        response = self.client.post(reverse('education:choice_create', args=[self.question.id]), {
            'text': 'Another Choice',
            'is_correct': False
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Student should not be able to create choices
        self.client.login(username='student', password='password123')
        response = self.client.post(reverse('education:choice_create', args=[self.question.id]), {
            'text': 'Student Choice',
            'is_correct': False
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
