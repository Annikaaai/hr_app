from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Аутентификация
    path('register/', views.register, name='register'),

    # Вакансии
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancies/create/', views.create_vacancy, name='create_vacancy'),

    # Стажировки
    path('internships/', views.internship_list, name='internship_list'),
    path('internships/create/', views.create_internship, name='create_internship'),

    # Дашборды
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/hr/', views.hr_dashboard, name='hr_dashboard'),
    path('dashboard/university/', views.university_dashboard, name='university_dashboard'),
    path('dashboard/applicant/', views.applicant_dashboard, name='applicant_dashboard'),

    # Профиль
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/applicant/create/', views.create_applicant_profile, name='create_applicant_profile'),
    path('profile/applicant/update/', views.update_applicant_profile, name='update_applicant_profile'),

    # Модерация
    path('moderation/', views.moderation_list, name='moderation_list'),
    path('moderation/vacancy/<int:pk>/<str:action>/', views.moderate_vacancy, name='moderate_vacancy'),
    path('moderation/internship/<int:pk>/<str:action>/', views.moderate_internship, name='moderate_internship'),

    # Аналитика
    path('analytics/', views.analytics, name='analytics'),
]