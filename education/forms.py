from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import Course, Module, Lesson, Exam, Question, Choice, Answer

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name'].split()[0]
        user.last_name = ' '.join(self.cleaned_data['full_name'].split()[1:])
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail', 'category', 'difficulty']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order', 'duration']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
            'duration': forms.TimeInput(format='%H:%M'),
        }

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'duration', 'due_date', 'total_marks', 'passing_marks']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'duration': forms.TimeInput(format='%H:%M'),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_type', 'text', 'marks', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text_answer']

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        
        if question:
            if question.question_type == 'mcq':
                self.fields['selected_choices'] = forms.ModelChoiceField(
                    queryset=question.choices.all(),
                    widget=forms.RadioSelect,
                    required=True
                )
            elif question.question_type == 'checkbox':
                self.fields['selected_choices'] = forms.ModelMultipleChoiceField(
                    queryset=question.choices.all(),
                    widget=forms.CheckboxSelectMultiple,
                    required=True
                )
            elif question.question_type in ['text', 'essay']:
                self.fields['text_answer'].widget = forms.Textarea(attrs={'rows': 4})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email_notifications', 'push_notifications']
        widgets = {
            'email_notifications': forms.CheckboxInput(),
            'push_notifications': forms.CheckboxInput(),
        } 