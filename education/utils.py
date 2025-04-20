from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import ExamSubmission, Answer, Question

def calculate_exam_score(submission):
    """
    Calculate the total score for an exam submission.
    """
    total_score = 0
    answers = Answer.objects.filter(submission=submission)
    
    for answer in answers:
        question = answer.question
        if question.question_type in ['mcq', 'checkbox']:
            # For multiple choice questions, check if all correct choices are selected
            correct_choices = set(question.choices.filter(is_correct=True))
            selected_choices = set(answer.selected_choices.all())
            
            if question.question_type == 'mcq':
                # For single choice, must match exactly
                if correct_choices == selected_choices:
                    total_score += question.marks
            else:
                # For multiple choice, partial credit based on correct selections
                correct_selections = len(correct_choices & selected_choices)
                incorrect_selections = len(selected_choices - correct_choices)
                if incorrect_selections == 0:
                    total_score += (correct_selections / len(correct_choices)) * question.marks
        else:
            # For text/essay questions, manual grading required
            pass
    
    submission.score = total_score
    submission.is_passed = total_score >= submission.exam.passing_marks
    submission.save()
    return total_score

def check_exam_permissions(user, exam):
    """
    Check if a user has permission to take an exam.
    """
    if user.role != 'student':
        raise PermissionDenied("Only students can take exams")
    
    if not exam.course.students.filter(id=user.id).exists():
        raise PermissionDenied("You are not enrolled in this course")
    
    if timezone.now() > exam.due_date:
        raise PermissionDenied("The exam deadline has passed")
    
    if ExamSubmission.objects.filter(user=user, exam=exam).exists():
        raise PermissionDenied("You have already submitted this exam")

def check_teacher_permissions(user, course):
    """
    Check if a user has permission to modify a course.
    """
    if user.role != 'teacher':
        raise PermissionDenied("Only teachers can modify courses")
    
    if course.instructor != user:
        raise PermissionDenied("You are not the instructor of this course")

def get_course_progress(user, course):
    """
    Calculate a user's progress in a course.
    """
    total_lessons = Lesson.objects.filter(module__course=course).count()
    if total_lessons == 0:
        return 0
    
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
        completed=True
    ).count()
    
    return (completed_lessons / total_lessons) * 100

def get_module_progress(user, module):
    """
    Calculate a user's progress in a module.
    """
    total_lessons = module.lessons.count()
    if total_lessons == 0:
        return 0
    
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__module=module,
        completed=True
    ).count()
    
    return (completed_lessons / total_lessons) * 100 