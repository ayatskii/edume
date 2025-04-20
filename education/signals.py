from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import ExamSubmission, LessonProgress, User
from .utils import calculate_exam_score

@receiver(post_save, sender=ExamSubmission)
def handle_exam_submission(sender, instance, created, **kwargs):
    """
    Handle actions after an exam submission is saved.
    """
    if created:
        # Calculate the score
        score = calculate_exam_score(instance)
        
        # Send email notification to student
        if instance.user.email_notifications:
            subject = f'Exam Submission Confirmation - {instance.exam.title}'
            message = f'''
            Dear {instance.user.get_full_name()},
            
            Your submission for the exam "{instance.exam.title}" has been received.
            Score: {score}/{instance.exam.total_marks}
            Status: {'Passed' if instance.is_passed else 'Failed'}
            
            Thank you for completing the exam.
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                fail_silently=True,
            )
        
        # Send email notification to instructor
        instructor = instance.exam.course.instructor
        if instructor.email_notifications:
            subject = f'New Exam Submission - {instance.exam.title}'
            message = f'''
            Dear {instructor.get_full_name()},
            
            A new submission has been received for the exam "{instance.exam.title}".
            Student: {instance.user.get_full_name()}
            Submitted at: {instance.submitted_at}
            
            Please review the submission in the admin panel.
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instructor.email],
                fail_silently=True,
            )

@receiver(post_save, sender=LessonProgress)
def handle_lesson_completion(sender, instance, created, **kwargs):
    """
    Handle actions when a lesson is marked as completed.
    """
    if instance.completed and not instance.completed_at:
        instance.completed_at = timezone.now()
        instance.save(update_fields=['completed_at'])
        
        # Send email notification to student
        if instance.user.email_notifications:
            subject = f'Lesson Completed - {instance.lesson.title}'
            message = f'''
            Dear {instance.user.get_full_name()},
            
            Congratulations! You have completed the lesson "{instance.lesson.title}".
            
            Keep up the good work!
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                fail_silently=True,
            )

@receiver(pre_save, sender=User)
def handle_user_role_change(sender, instance, **kwargs):
    """
    Handle actions when a user's role is changed.
    """
    if instance.pk:  # Only for existing users
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.role != instance.role:
                # Send email notification about role change
                subject = 'Account Role Update'
                message = f'''
                Dear {instance.get_full_name()},
                
                Your account role has been changed to {instance.get_role_display()}.
                
                This change may affect your access to certain features of the system.
                '''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
        except User.DoesNotExist:
            pass 