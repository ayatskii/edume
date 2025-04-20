from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import User, Course, Module, Lesson, LessonProgress, Exam, Question, Choice, ExamSubmission, Answer
from .forms import (
    UserRegistrationForm, CourseForm, ModuleForm, LessonForm, ExamForm,
    QuestionForm, ChoiceForm, AnswerForm, UserProfileForm, NotificationPreferencesForm
)

def home(request):
    """Home page view for the education system"""
    # Simplified view just to get it working
    return render(request, 'education/home.html', {
        'featured_courses': []
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('education:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'education/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('education:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'education/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('education:login')

@login_required(login_url='education:login')
def dashboard(request):
    if request.user.role == 'teacher':
        teacher_courses = Course.objects.filter(instructor=request.user)
        upcoming_exams = Exam.objects.filter(course__instructor=request.user)
        context = {
            'teacher_courses': teacher_courses,
            'upcoming_exams': upcoming_exams.filter(due_date__gt=timezone.now()),
        }
    else:
        enrolled_courses = request.user.courses_enrolled.all()
        upcoming_exams = Exam.objects.filter(course__in=enrolled_courses)
        
        # Calculate course progress
        course_progress = {}
        for course in enrolled_courses:
            total_lessons = 0
            completed_lessons = 0
            for module in course.modules.all():
                lessons = module.lessons.count()
                total_lessons += lessons
                completed_lessons += LessonProgress.objects.filter(
                    user=request.user,
                    lesson__module=module,
                    completed=True
                ).count()
            
            if total_lessons > 0:
                progress = int((completed_lessons / total_lessons) * 100)
            else:
                progress = 0
            
            course_progress[course.id] = progress
            
        context = {
            'enrolled_courses': enrolled_courses,
            'upcoming_exams': upcoming_exams.filter(due_date__gt=timezone.now()),
            'course_progress': course_progress
        }
    
    return render(request, 'education/dashboard.html', context)

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'education/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return Course.objects.filter(instructor=self.request.user)
        return Course.objects.filter(students=self.request.user)

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'education/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.all()
        context['exams'] = self.object.exams.all()
        
        if self.request.user.role == 'student':
            # Calculate module progress
            module_progress = {}
            for module in self.object.modules.all():
                total_lessons = module.lessons.count()
                if total_lessons > 0:
                    completed_lessons = LessonProgress.objects.filter(
                        user=self.request.user,
                        lesson__module=module,
                        completed=True
                    ).count()
                    progress = int((completed_lessons / total_lessons) * 100)
                else:
                    progress = 0
                module_progress[module.id] = progress
            
            context['module_progress'] = module_progress
        
        return context

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.user.role != 'student':
        messages.error(request, 'Only students can enroll in courses')
        return redirect('education:course_detail', pk=course.pk)
    
    if request.user in course.students.all():
        messages.info(request, 'You are already enrolled in this course')
    else:
        course.students.add(request.user)
        messages.success(request, f'Successfully enrolled in {course.title}')
    
    return redirect('education:course_detail', pk=course.pk)

class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'education/course_form.html'
    success_url = reverse_lazy('education:course_list')

    def test_func(self):
        return self.request.user.role == 'teacher'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

class ModuleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'education/module_form.html'

    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return self.request.user == course.instructor

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('education:course_detail', kwargs={'pk': self.kwargs['course_id']})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs['course_id']
        return context

class LessonCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'education/lesson_form.html'

    def test_func(self):
        module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return self.request.user == module.course.instructor

    def form_valid(self, form):
        form.instance.module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return super().form_valid(form)

    def get_success_url(self):
        module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return reverse_lazy('education:course_detail', kwargs={'pk': module.course.pk})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return context

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    module = lesson.module
    
    # Get previous and next lessons for navigation
    all_lessons = list(module.lessons.order_by('order'))
    lesson_index = all_lessons.index(lesson)
    previous_lesson = all_lessons[lesson_index - 1] if lesson_index > 0 else None
    next_lesson = all_lessons[lesson_index + 1] if lesson_index < len(all_lessons) - 1 else None
    
    # Calculate module progress
    if request.user.role == 'student':
        total_lessons = module.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__module=module,
            completed=True
        ).count()
        
        if total_lessons > 0:
            module_progress = int((completed_lessons / total_lessons) * 100)
        else:
            module_progress = 0
        
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': False}
        )
    else:
        progress = None
        module_progress = 0
    
    context = {
        'lesson': lesson,
        'progress': progress,
        'module_progress': module_progress,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson
    }
    
    return render(request, 'education/lesson_detail.html', context)

@login_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.user.role == 'student':
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True, 'completed_at': timezone.now()}
        )
        if not created and not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            messages.success(request, 'Lesson marked as complete')
    return redirect('education:lesson_detail', pk=pk)

class ExamCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'education/exam_form.html'

    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return self.request.user == course.instructor

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('education:exam_detail', kwargs={'pk': self.object.pk})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs['course_id']
        return context

class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'education/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'student':
            context['submission'] = ExamSubmission.objects.filter(
                user=self.request.user,
                exam=self.object
            ).first()
        return context

@login_required
def take_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.user.role != 'student':
        messages.error(request, 'Only students can take exams')
        return redirect('education:exam_detail', pk=pk)

    submission = ExamSubmission.objects.filter(user=request.user, exam=exam).first()
    if submission:
        messages.error(request, 'You have already submitted this exam')
        return redirect('education:exam_detail', pk=pk)

    if request.method == 'POST':
        submission = ExamSubmission.objects.create(
            user=request.user,
            exam=exam,
            submitted_at=timezone.now()
        )
        
        total_score = 0
        for question in exam.questions.all():
            answer_form = AnswerForm(request.POST, question=question, prefix=f'question_{question.pk}')
            if answer_form.is_valid():
                answer = answer_form.save(commit=False)
                answer.submission = submission
                answer.question = question
                
                # Calculate score based on question type
                if question.question_type == 'mcq':
                    selected_choice = answer_form.cleaned_data.get('selected_choices')
                    if selected_choice and selected_choice.is_correct:
                        answer.score = question.marks
                    else:
                        answer.score = 0
                elif question.question_type == 'checkbox':
                    selected_choices = answer_form.cleaned_data.get('selected_choices', [])
                    correct_choices = question.choices.filter(is_correct=True)
                    incorrect_choices = question.choices.filter(is_correct=False)
                    
                    # Check if all correct choices are selected and no incorrect choices
                    if (all(choice in selected_choices for choice in correct_choices) and 
                        not any(choice in selected_choices for choice in incorrect_choices)):
                        answer.score = question.marks
                    else:
                        answer.score = 0
                else:  # text or essay questions - will need manual grading
                    answer.score = 0  # Default to 0 until manually graded
                
                total_score += answer.score
                answer.save()

        # Update submission score and status
        submission.score = total_score
        submission.is_passed = total_score >= exam.passing_marks
        submission.save()
        
        messages.success(request, 'Exam submitted successfully!')
        return redirect('education:exam_detail', pk=pk)

    questions = exam.questions.all().order_by('order')
    forms = []
    for question in questions:
        form = AnswerForm(prefix=f'question_{question.pk}', question=question)
        forms.append((question, form))

    return render(request, 'education/take_exam.html', {
        'exam': exam,
        'questions_and_forms': forms
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('education:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'education/profile.html', {'form': form})

@login_required
def notification_preferences(request):
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated!')
            return redirect('education:notification_preferences')
    else:
        form = NotificationPreferencesForm(instance=request.user)
    return render(request, 'education/notification_preferences.html', {'form': form})

class QuestionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'education/question_form.html'
    
    def test_func(self):
        exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return self.request.user == exam.course.instructor
    
    def form_valid(self, form):
        form.instance.exam = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.object.question_type in ['mcq', 'checkbox']:
            return reverse_lazy('education:choice_create', kwargs={'question_id': self.object.pk})
        return reverse_lazy('education:exam_detail', kwargs={'pk': self.kwargs['exam_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return context

class ChoiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Choice
    form_class = ChoiceForm
    template_name = 'education/choice_form.html'
    
    def test_func(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return self.request.user == question.exam.course.instructor
    
    def form_valid(self, form):
        form.instance.question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return super().form_valid(form)
    
    def get_success_url(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        
        # If user clicks "Add Another"
        if 'add_another' in self.request.POST:
            return reverse_lazy('education:choice_create', kwargs={'question_id': self.kwargs['question_id']})
        
        # Otherwise go back to exam detail
        return reverse_lazy('education:exam_detail', kwargs={'pk': question.exam.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        context['question'] = question
        context['choices'] = question.choices.all()
        
        # Check if a correct choice already exists for MCQ questions
        if question.question_type == 'mcq':
            context['correct_exists'] = question.choices.filter(is_correct=True).exists()
        
        return context
