from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Count, Q, Avg
import json
from django.contrib.auth.decorators import login_required
import json
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
# Import models explicitly
from django.contrib.auth.models import User, Group
from management.models import *
from students.models import *
from exam.models import *
from main.models import *

from django.core.mail import send_mail
import random
import string

def generate_random_string(length=4):
    """Generate a random string of numbers and letters."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def teacher_signup_view(request):
    colleges = Clg.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        college_id = request.POST.get('college_name')
        course = request.POST.get('course').strip()
        profile_pic = request.FILES.get('profile_pic')

        # Get college name
        college = Clg.objects.get(id=college_id) if college_id else None
        college_name = college.clg_name if college else ""

        # Generate a unique username
        base_username = f"{first_name.lower()}{last_name.lower()}"
        unique_string = generate_random_string()
        username = f"{base_username}{unique_string}"

        # Ensure the username is unique
        while User.objects.filter(username=username).exists():
            unique_string = generate_random_string()
            username = f"{base_username}{unique_string}"

        # Generate a random password
        password = f"MGA@{random.randint(1000, 9999)}"

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('teacher_signup')

        # Create the user
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)

        # Create the teacher profile
        teacher = Management.objects.create(user=user, email=email, college_name=college_name, course=course, profile_pic=profile_pic)

        # Assign the user to the 'TEACHER' group
        my_teacher_group, created = Group.objects.get_or_create(name='TEACHER')
        my_teacher_group.user_set.add(user)

        # Send login credentials via email
        subject = "Your Teacher Account Credentials"
        message = f"""
Hello {first_name},

Your teacher account has been created successfully.

Username: {username}
Password: {password}

Please log in and change your password after logging in.

Best regards,
Admin Team
"""
        send_mail(subject, message, 'aspirantcbe@gmail.com', [email])

        messages.success(request, "Signup successful! Your credentials have been sent via email. Wait for admin approval.")
        return redirect('teacherlogin')

    return render(request, 'teachers/teachersignup.html', {'colleges': colleges})



def teacher_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            teacher = Management.objects.filter(user=user).first()
            if teacher and teacher.is_approved:
                login(request, user)
                return redirect('teacher_dashboard')  # Redirect to teacher index page
            else:
                messages.error(request, "Your account is pending admin approval.")
                return redirect('teacherlogin')
        else:
            messages.error(request, "Invalid credentials!")
    
    return render(request, 'teachers/teacherlogin.html')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_teachers(request):
    pending_teachers = Management.objects.filter(is_approved=False)
    
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        teacher = Management.objects.get(id=teacher_id)
        teacher.is_approved = True
        teacher.save()
        messages.success(request, f"{teacher.user.first_name} is now approved.")
        return redirect('approve_teachers')  # Refresh after approval

    return render(request, 'admin/approve_teachers.html', {'pending_teachers': pending_teachers})

# Dashboard for Management

from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count, Q, Avg
from django.utils.timezone import now
import json
@login_required
def teacher_dashboard(request):
    # Get the logged-in teacher's details
    teacher = get_object_or_404(Management, user=request.user)
    print(f"afafafa{teacher}")

    # Redirect if not approved
    if not teacher.is_approved:
        return redirect('teacherlogin')
    
    syllabus_data = {}
    colleges = Clg.objects.filter(clg_name=teacher.college_name)
    print(colleges)

    # syllabus datacolection
    for college in colleges:
        syllabus_data[college.clg_name] = Syllabus.objects.filter(clg=college).order_by("day")
        for i in syllabus_data:
            print(syllabus_data[i])

    # 📌 Get the logged-in teacher's college name
    user_college = teacher.college_name

    # 📌 Filter students based on the teacher's college
    students_in_college = Student.objects.filter(clg=user_college)

    # 📌 Group students by department
    department_wise_students = (
        students_in_college
        .values('dep__name')  # Fetch department names
        .annotate(total_students=Count('id'))
    )

    # 📌 Attendance summary (for today)
    today = now().date()
    attendance_summary = (
        students_in_college
        .values('dep__name')  # Group by department
        .annotate(
            total_students=Count('id'),
            present=Count('attendance', filter=Q(attendance__date=today, attendance__status=True)),
            absent=Count('attendance', filter=Q(attendance__date=today, attendance__status=False))
        )
    )

    # Convert attendance data for frontend
    attendance_data = []
    departments = []
    attendance_percentages = []

    for record in attendance_summary:
        total = record['total_students']
        present = record['present']
        percentage = (present / total * 100) if total > 0 else 0

        attendance_data.append({
            'department': record['dep__name'],
            'total_students': total,
            'present': present,
            'absent': record['absent'],
            'attendance_percentage': round(percentage, 2)
        })

        departments.append(record['dep__name'])
        attendance_percentages.append(round(percentage, 2))

    # 📌 Exam results (average marks per department)
    exam_query = (
        Result.objects.filter(student__clg=user_college)
        .values('student__dep__name')  # Fetch department names
        .annotate(avg_marks=Avg('marks'))
    )
    print(exam_query)
    # Extract department-wise exam data
    exam_department_names = [result['student__dep__name'] for result in exam_query]
    print(exam_department_names)

    exam_avg_marks = [round(result['avg_marks'], 2) for result in exam_query]

    print(exam_avg_marks)

    request.session["attendance_data"] = attendance_data

    context = {
        "department_wise_students": department_wise_students,
        "attendance_data": attendance_data,
        "departments": json.dumps(departments),
        "attendance_percentages": json.dumps(attendance_percentages),
        "exam_department_names": json.dumps(exam_department_names),
        "exam_avg_marks": json.dumps(exam_avg_marks),
        "syllabus_data": syllabus_data,
    }

    return render(request, 'teachers/dashboard.html', context)

import pandas as pd
from django.http import HttpResponse
import datetime

def download_attendance_excel(request):
    # Fetch attendance data from session/context
    attendance_data = request.session.get("attendance_data", [])

    if not attendance_data:
        return HttpResponse("No data available", content_type="text/plain")

    # Convert to DataFrame
    df = pd.DataFrame(attendance_data)

    # Create response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=attendance_{datetime.date.today()}.xlsx"

    # Convert DataFrame to Excel and write to response
    with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance Data")

    return response


@login_required
def student_list(request):
    teacher = get_object_or_404(Management, user=request.user)
    # print("Teacher College Name:", teacher.college_name)
    students = Student.objects.filter(clg=teacher.college_name)  # Now 'college' is a Clg instance
    # print("Students List:", students)
    return render(request, 'teachers/students_list.html', {'students': students})

@login_required
def syllabus_view(request):
    if request.method == "POST":
        clg_id = request.POST.get("clg")  # Get College ID
        day = request.POST.get("day")  # Get Day
        topic = request.POST.get("topic")  # Get Topic
        trainer_name = request.POST.get("trainer_name")  # Get Trainer Name

        if clg_id and day and topic and trainer_name:
            clg = Clg.objects.get(id=clg_id)  # Fetch the college object
            # Save syllabus entry
            Syllabus.objects.create(clg=clg, day=day, topic=topic, trainer_name=trainer_name)
            return redirect("syllabus")  # Redirect to avoid duplicate submissions

    # Retrieve all syllabus items grouped by college
    syllabus_data = {}
    colleges = Clg.objects.all()

    for college in colleges:
        syllabus_data[college.clg_name] = Syllabus.objects.filter(clg=college).order_by("day")

    return render(request, "admin/dashboard.html", {"syllabus_data": syllabus_data, "colleges": colleges})

def mark_attendance(request):
    management = get_object_or_404(Management, user=request.user) # Get the logged-in teacher
    students = Student.objects.filter(clg=management.college_name)# Fetch students from the same college
    today = date.today()  # Get the current date

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("student_"):  
                student_id = key.replace("student_", "")  # Extract student ID
                student = students.filter(id=student_id).first()  # Ensure only valid students are processed
                
                if student:
                    status = True if value.lower() == "present" else False
                    
                    # Check if an attendance record already exists for this student and date
                    attendance = Attendance.objects.filter(student=student, date=today).first()

                    if attendance:
                        attendance.status = status  # Update status
                        attendance.save()
                    else:
                        Attendance.objects.create(student=student, date=today, status=status)  # Create new record

        return redirect('teacher_dashboard')

    return render(request, 'admin/mark_attendance.html', {'students': students})

def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, user=user)
    results = Result.objects.filter(student=student)

    return render(request, 'admin/std_profile.html', {'user': user, 'student': student, 'results': results})

def user_logout(request):
    logout(request)
    return redirect('login')