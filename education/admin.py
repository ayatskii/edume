from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Course, Module, Lesson, LessonProgress,
    Exam, Question, Choice, ExamSubmission, Answer
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Notifications', {'fields': ('email_notifications', 'push_notifications')}),
    )

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'difficulty', 'created_at')
    list_filter = ('category', 'difficulty', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    inlines = [ModuleInline]

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'content')

class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'completed_at')
    search_fields = ('user__username', 'lesson__title')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'question_type', 'marks', 'order')
    list_filter = ('exam', 'question_type')
    search_fields = ('text',)
    inlines = [ChoiceInline]

class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration', 'due_date', 'total_marks')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'text_answer', 'selected_choices')

class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'submitted_at', 'score', 'is_passed')
    list_filter = ('exam', 'submitted_at', 'is_passed')
    search_fields = ('user__username', 'exam__title')
    inlines = [AnswerInline]

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonProgress, LessonProgressAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ExamSubmission, ExamSubmissionAdmin)
