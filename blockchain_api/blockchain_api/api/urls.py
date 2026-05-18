from django.urls import path
from . import views

urlpatterns = [
    path('store_user_profile/', views.store_user_profile, name='store_user_profile'),
    path('get_user_profile/', views.get_user_profile, name='get_user_profile'),
    path('get_user_profile_by_username/', views.get_user_profile_by_username, name='get_user_profile_by_username'),
    path('store_lab_report/', views.store_lab_report, name='store_lab_report'),
    path('get_lab_reports/', views.get_lab_reports, name='get_lab_reports'),
    path('store_doctor_profile/', views.store_doctor_profile, name='store_doctor_profile'),
    path('get_doctor_profile/', views.get_doctor_profile, name='get_doctor_profile'),
    path('get_my_access_code/', views.get_my_access_code, name='get_my_access_code'),
]