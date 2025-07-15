# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.select_course, name='select_course'),
    # path('start_exam/<int:course_id>/<int:num_questions>/', views.start_exam, name='start_exam'),
    # path('profile/', views.profile, name='profile'),
    # path('execute/', views.execute_code, name='execute_code'),
    path('compiler/', views.compiler, name='compiler'),
    # path('run_code/', views.run_code, name='runcode'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)