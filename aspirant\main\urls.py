from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.pdf_list, name="pdf_list"),
    path('pdfs/<int:pdf_id>/', views.pdf_detail, name='pdf_detail'),

    path("upload/",  views.upload_questions_docx, name="upload_questions"),
    path('',views.index,name="index"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

