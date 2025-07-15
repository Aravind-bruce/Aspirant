from django.db import models
from django.contrib.auth.models import User
from main.models import *

class Management(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='Management/profile_pic/', null=True, blank=True)
    status = models.BooleanField(default=False)  # Active or Inactive
    email = models.EmailField(unique=True)
    college_name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)  # Approval from Superuser

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.user.first_name

class Syllabus(models.Model):
    SESSION_CHOICES = [
        ('FN', 'Forenoon'),
        ('AN', 'Afternoon'),
    ]

    clg = models.ForeignKey(Clg, on_delete=models.CASCADE)  # Link syllabus to a specific college
    day = models.IntegerField()  # Day number
    session = models.CharField(max_length=2, choices=SESSION_CHOICES, default='FN')  # FN or AN session
    topic = models.CharField(max_length=255)  # Syllabus topic
    trainer_name = models.CharField(max_length=100)  # Trainer conducting the session

    class Meta:
        unique_together = ('clg', 'day', 'session')  # Ensures no duplicate day+session entries for the same college

    def __str__(self):
        return f"{self.clg.clg_name} - Day {self.day} ({self.session}): {self.topic} (Trainer: {self.trainer_name})"



