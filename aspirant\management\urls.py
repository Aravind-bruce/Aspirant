from django.urls import path
from . import views

urlpatterns = [
    path('teacher_signup/', views.teacher_signup_view, name='teacher_signup'),
    path('', views.teacher_login_view, name='teacherlogin'),
    path('approve_teachers/', views.approve_teachers, name='approve_teachers'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('students/', views.student_list, name='students-list'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    # path('class-wise-attendance/', views.department_wise_performance, name='class_wise_attendance'),
    path('view_profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('logout/', views.user_logout, name='user_logout'),
    path("download-attendance/", views.download_attendance_excel, name="download_attendance"),
]

