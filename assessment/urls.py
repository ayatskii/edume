from django.urls import path
from education import views as education_views

app_name = 'assessment'

urlpatterns = [
    # Exams
    path('course/<int:course_id>/exam/create/', education_views.ExamCreateView.as_view(), name='exam_create'),
    path('exam/<int:pk>/', education_views.ExamDetailView.as_view(), name='exam_detail'),
    path('exam/<int:pk>/take/', education_views.take_exam, name='take_exam'),
    path('exam/<int:pk>/delete/', education_views.ExamDeleteView.as_view(), name='exam_delete'),
    
    # Questions and Choices
    path('exam/<int:exam_id>/question/create/', education_views.QuestionCreateView.as_view(), name='question_create'),
    path('question/<int:question_id>/choice/create/', education_views.ChoiceCreateView.as_view(), name='choice_create'),
] 