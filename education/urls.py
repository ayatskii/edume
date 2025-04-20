from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    # Home page is handled in the main urls.py files
    # path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notification_preferences, name='notification_preferences'),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Modules
    path('course/<int:course_id>/module/create/', views.ModuleCreateView.as_view(), name='module_create'),
    
    # Lessons
    path('module/<int:module_id>/lesson/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    
    # Exams
    path('course/<int:course_id>/exam/create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('exam/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('exam/<int:pk>/take/', views.take_exam, name='take_exam'),
    
    # Questions and Choices
    path('exam/<int:exam_id>/question/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('question/<int:question_id>/choice/create/', views.ChoiceCreateView.as_view(), name='choice_create'),
] 