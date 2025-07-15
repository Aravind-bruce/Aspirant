from django.db import models

from students.models import Student
from datetime import time

from django.db import models
from datetime import time, datetime

from datetime import datetime, time

class Course(models.Model):
    COURSE_GROUPS = [
        ('Aptitude & Reasoning', 'Aptitude & Reasoning'),
        ('Communication & Soft Skill', 'Communication & Soft Skill'),
        ('Aptitude & Soft Skill', 'Aptitude & Soft Skill'),
        ('Technical', 'Technical'),
    ]
    
    course_group = models.CharField(max_length=50, choices=COURSE_GROUPS, default='Aptitude')
    course_name = models.CharField(max_length=50)
    question_number = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    is_approved = models.BooleanField(default=False)

    exam_start_time = models.TimeField(
        default=time(9, 0),  # Default start time: 9:00 AM
        help_text="Enter exam start time in HH:MM:SS format"
    )
    
    exam_end_time = models.TimeField(
        default=time(10, 30),  # Default end time: 10:30 AM
        help_text="Enter exam end time in HH:MM:SS format"
    )

    def __str__(self):
        return f"{self.course_name} ({self.course_group})"

    def formatted_exam_start_time(self):
        return self.exam_start_time.strftime('%I:%M %p')  # 12-hour format

    def formatted_exam_end_time(self):
        return self.exam_end_time.strftime('%I:%M %p')  # 12-hour format

    def exam_duration(self):
        """Calculate exam duration and return it in hours and minutes."""
        start = datetime.combine(datetime.today(), self.exam_start_time)
        end = datetime.combine(datetime.today(), self.exam_end_time)
        duration = end - start
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        return f"{hours} hr {minutes} min" if minutes else f"{hours} hr"


class Question(models.Model):
    PRIORITY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    cat = (('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4'))
    answer = models.CharField(max_length=200, choices=cat)
    reason = models.TextField(default="No explanation provided.", blank=True, null=True)
    
    # **New Priority Field**
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')

    def __str__(self):
        return f"{self.question} ({self.priority})"
    
class Clg(models.Model):
    clg_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.clg_name

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
