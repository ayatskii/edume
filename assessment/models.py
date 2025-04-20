from django.db import models

# Create your models here.

class AssessmentConfig(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    
    def __str__(self):
        return self.name
