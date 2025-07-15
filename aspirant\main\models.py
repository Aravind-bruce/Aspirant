from django.db import models
from django.shortcuts import render
from django.core.validators import FileExtensionValidator

class FileUpload(models.Model):
    folder_path = models.CharField(max_length=255)  # Store full folder path
    file = models.FileField(upload_to='uploads/')  # File storage
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.folder_path}/{self.file.name}"

class Sources(models.Model):
    COURSE_CHOICES = [
        ('Aptitude & Reasoning', 'Aptitude & Reasoning'),
        ('Communication & Soft Skill', 'Communication & Soft Skill'),
        ('Aptitude & Soft Skill', 'Aptitude & Soft Skill'),
        ('Technical', 'Technical'),
    ]
    course_name =  models.CharField(max_length=100, choices=COURSE_CHOICES, default='Aptitude & Reasoning')

    def __str__(self):
        return self.course_name
    

class Notes(models.Model):
    NOTE_TYPES = [
        ('class', 'Class Notes'),
        ('test', 'Test Notes'),
        ('infographic', 'Infographic Notes'),
    ]
    
    course = models.ForeignKey(Sources, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="uploads/notes/",
        validators=[FileExtensionValidator(['pdf', 'docx', 'png', 'jpg'])]
    )
    title = models.CharField(max_length=255, blank=True)
    note_type = models.CharField(max_length=15, choices=NOTE_TYPES)
    subtitle_text = models.CharField(max_length=255, blank=True, null=True)  # Subtitle merged here
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_note_type_display()} - {self.title}"

class Source_file(models.Model):
    course=models.ForeignKey(Sources,on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="uploads/",
        validators=[FileExtensionValidator(['pdf', 'docx'])]
    )
    title = models.CharField(max_length=255, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Clg(models.Model):
    COURSE_CHOICES = [
        ('Aptitude & Reasoning', 'Aptitude & Reasoning'),
        ('Communication & Soft Skill', 'Communication & Soft Skill'),
        ('Aptitude & Soft Skill', 'Aptitude & Soft Skill'),
        ('Technical', 'Technical'),
    ]

    clg_name = models.CharField(max_length=100, unique=True)  # Removed default=1
    course_name = models.CharField(max_length=100, choices=COURSE_CHOICES, default='Aptitude & Reasoning')

    def __str__(self):
        return self.clg_name

class Department(models.Model):
    clg = models.ForeignKey(Clg, on_delete=models.CASCADE)  # Check if this exists
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.clg.clg_name}"

class ClassModule(models.Model):
    clg = models.ForeignKey(Clg, on_delete=models.CASCADE, related_name="class_modules")  # Changed OneToOneField to ForeignKey
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="classes")
    class_name = models.CharField(max_length=20, default='A')  # Example: CSE(A), CSE(B)

    def __str__(self):
        return f"{self.department.name} ({self.class_name})"

