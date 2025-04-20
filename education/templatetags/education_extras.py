from django import template
from django.db.models import Count

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def student_count(course):
    """
    Return the number of students enrolled in a course.
    Usage: {{ course|student_count }}
    """
    if hasattr(course, 'students'):
        return course.students.count()
    return 0

@register.filter
def count_unique_students(courses):
    """
    Count unique students across multiple courses.
    Usage: {{ courses|count_unique_students }}
    """
    student_set = set()
    for course in courses:
        for student in course.students.all():
            student_set.add(student.id)
    return len(student_set)

@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to a form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class}) 