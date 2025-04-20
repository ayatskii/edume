from .models import Course, Exam

def user_courses(request):
    """Context processor to add enrolled courses and created courses to the context."""
    context = {
        'enrolled_courses': [],
        'created_courses': []
    }
    
    if request.user.is_authenticated:
        if request.user.role == 'student':
            context['enrolled_courses'] = request.user.courses_enrolled.all()
        elif request.user.role == 'teacher':
            context['created_courses'] = Course.objects.filter(instructor=request.user)
    
    return context

def upcoming_exams(request):
    """Context processor to add upcoming exams to the context."""
    context = {
        'upcoming_exams': []
    }
    
    if request.user.is_authenticated:
        if request.user.role == 'student':
            context['upcoming_exams'] = Exam.objects.filter(
                course__in=request.user.courses_enrolled.all()
            ).order_by('due_date')[:5]
        elif request.user.role == 'teacher':
            context['upcoming_exams'] = Exam.objects.filter(
                course__instructor=request.user
            ).order_by('due_date')[:5]
    
    return context

def user_role(request):
    """Context processor to add user role to the context."""
    context = {
        'is_student': False,
        'is_teacher': False
    }
    
    if request.user.is_authenticated:
        context['is_student'] = request.user.role == 'student'
        context['is_teacher'] = request.user.role == 'teacher'
    
    return context 