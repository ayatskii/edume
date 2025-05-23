# Generated by Django 5.2 on 2025-04-21 00:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0002_alter_examsubmission_user_alter_user_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_taught', to='education.user'),
        ),
        migrations.AlterField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='courses_enrolled', to='education.user'),
        ),
        migrations.AlterField(
            model_name='lessonprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to='education.user'),
        ),
    ]
