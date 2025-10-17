from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import *
from .forms import *
from django.contrib.auth import login
from django.shortcuts import render, redirect


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()

            # Автоматически входим после регистрации
            login(request, user)

            # Профиль уже создан сигналом, просто обновляем роль если нужно
            try:
                user_profile = user.userprofile
                # Убедимся, что роль установлена как 'applicant'
                if user_profile.role != 'applicant':
                    user_profile.role = 'applicant'
                    user_profile.save()
            except UserProfile.DoesNotExist:
                # На всякий случай, если сигнал не сработал
                UserProfile.objects.create(user=user, role='applicant')

            messages.success(request, 'Регистрация прошла успешно! Заполните ваш профиль.')
            return redirect('profile_setup')
    else:
        user_form = CustomUserCreationForm()

    context = {'form': user_form}
    return render(request, 'registration/register.html', context)

def is_admin(user):
    try:
        return user.userprofile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False

def is_hr(user):
    try:
        return user.userprofile.role == 'hr'
    except UserProfile.DoesNotExist:
        return False

def is_university(user):
    try:
        return user.userprofile.role == 'university'
    except UserProfile.DoesNotExist:
        return False


def home(request):
    try:
        vacancies = Vacancy.objects.filter(status='published')[:6]
        internships = Internship.objects.filter(status='published')[:6]
    except models.OperationalError:
        # Если таблицы еще не созданы
        vacancies = []
        internships = []
        messages.info(request, "База данных инициализируется. Некоторые функции могут быть временно недоступны.")

    context = {
        'vacancies': vacancies,
        'internships': internships,
    }
    return render(request, 'career_app/home.html', context)


def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='published')

    # Фильтрация
    query = request.GET.get('q')
    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__name__icontains=query)
        )

    paginator = Paginator(vacancies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'career_app/vacancy_list.html', context)


def vacancy_detail(request, pk):
    try:
        # Пытаемся найти опубликованную вакансию
        vacancy = Vacancy.objects.get(pk=pk, status='published')
    except Vacancy.DoesNotExist:
        # Если вакансия не опубликована, проверяем права доступа
        vacancy = get_object_or_404(Vacancy, pk=pk)

        # Проверяем, имеет ли пользователь право просматривать эту вакансию
        can_view = False

        if request.user.is_authenticated:
            # HR может просматривать вакансии своей компании
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'hr':
                if vacancy.company == request.user.userprofile.company:
                    can_view = True

            # Администратор может просматривать все вакансии
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                can_view = True

        if not can_view:
            messages.error(request, 'У вас нет прав для просмотра этой вакансии или она еще не опубликована.')
            return redirect('vacancy_list')

    # Проверяем, может ли пользователь откликаться на вакансию
    can_apply = vacancy.status == 'published'

    if request.method == 'POST' and can_apply:
        if not request.user.is_authenticated:
            applicant_form = ApplicantForm(request.POST, request.FILES)
            if applicant_form.is_valid():
                applicant = applicant_form.save()
                application = Application.objects.create(
                    vacancy=vacancy,
                    applicant=applicant,
                    cover_letter=request.POST.get('cover_letter', '')
                )
                messages.success(request, 'Ваш отклик успешно отправлен!')
                return redirect('vacancy_detail', pk=pk)
        else:
            try:
                applicant = request.user.applicant
                application = Application.objects.create(
                    vacancy=vacancy,
                    applicant=applicant,
                    cover_letter=request.POST.get('cover_letter', '')
                )
                messages.success(request, 'Ваш отклик успешно отправлен!')
                return redirect('vacancy_detail', pk=pk)
            except Applicant.DoesNotExist:
                messages.error(request, 'Пожалуйста, заполните ваш профиль соискателя.')
                return redirect('create_applicant_profile')

    applicant_form = ApplicantForm()

    context = {
        'vacancy': vacancy,
        'applicant_form': applicant_form,
        'can_apply': can_apply,
    }
    return render(request, 'career_app/vacancy_detail.html', context)

def internship_list(request):
    internships = Internship.objects.filter(status='published')

    query = request.GET.get('q')
    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(specialty__icontains=query)
        )

    paginator = Paginator(internships, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'career_app/internship_list.html', context)


@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Перенаправляем на страницу настройки профиля
        messages.info(request, "Пожалуйста, завершите настройку вашего профиля.")
        return redirect('profile_setup')

    if user_profile.role == 'admin':
        return admin_dashboard(request)
    elif user_profile.role == 'hr':
        return hr_dashboard(request)
    elif user_profile.role == 'university':
        return university_dashboard(request)
    else:
        return applicant_dashboard(request)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Статистика для администратора
    vacancies_count = Vacancy.objects.count()
    published_vacancies = Vacancy.objects.filter(status='published').count()
    moderation_vacancies = Vacancy.objects.filter(status='moderation').count()

    internships_count = Internship.objects.count()
    published_internships = Internship.objects.filter(status='published').count()
    moderation_internships = Internship.objects.filter(status='moderation').count()

    applications_count = Application.objects.count()
    total_companies = Company.objects.count()

    context = {
        'vacancies_count': vacancies_count,
        'published_vacancies': published_vacancies,
        'moderation_vacancies': moderation_vacancies,
        'internships_count': internships_count,
        'published_internships': published_internships,
        'moderation_internships': moderation_internships,
        'applications_count': applications_count,
        'total_companies': total_companies,
    }
    return render(request, 'career_app/admin_dashboard.html', context)

@login_required
@user_passes_test(is_hr)
def hr_dashboard(request):
    company = request.user.userprofile.company
    vacancies = Vacancy.objects.filter(company=company)
    applications = Application.objects.filter(vacancy__company=company)

    # Статистика
    vacancies_published = vacancies.filter(status='published').count()
    vacancies_moderation = vacancies.filter(status='moderation').count()

    context = {
        'company': company,
        'vacancies': vacancies,
        'applications': applications,
        'vacancies_published': vacancies_published,
        'vacancies_moderation': vacancies_moderation,
    }
    return render(request, 'career_app/hr_dashboard.html', context)

@login_required
@user_passes_test(is_university)
def university_dashboard(request):
    institution = request.user.userprofile.institution
    internships = Internship.objects.filter(institution=institution)

    # Статистика
    internships_published = internships.filter(status='published').count()
    internships_moderation = internships.filter(status='moderation').count()

    context = {
        'institution': institution,
        'internships': internships,
        'internships_published': internships_published,
        'internships_moderation': internships_moderation,
    }
    return render(request, 'career_app/university_dashboard.html', context)

@login_required
def applicant_dashboard(request):
    try:
        applicant = request.user.applicant
        applications = Application.objects.filter(applicant=applicant)
    except Applicant.DoesNotExist:
        applicant = None
        applications = []

    context = {
        'applicant': applicant,
        'applications': applications,
    }
    return render(request, 'career_app/applicant_dashboard.html', context)


@login_required
@user_passes_test(is_hr)
def create_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.company = request.user.userprofile.company
            vacancy.created_by = request.user
            vacancy.status = 'moderation'
            vacancy.save()
            messages.success(request, 'Вакансия отправлена на модерацию!')
            return redirect('hr_dashboard')  # Исправлено здесь
    else:
        form = VacancyForm()

    context = {'form': form}
    return render(request, 'career_app/vacancy_form.html', context)


@login_required
@user_passes_test(is_university)
def create_internship(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.institution = request.user.userprofile.institution
            internship.created_by = request.user
            internship.status = 'moderation'
            internship.save()
            messages.success(request, 'Заявка на стажировку отправлена на модерацию!')
            return redirect('university_dashboard')  # Исправлено здесь
    else:
        form = InternshipForm()

    context = {'form': form}
    return render(request, 'career_app/internship_form.html', context)

@login_required
@user_passes_test(is_admin)
def moderation_list(request):
    vacancies = Vacancy.objects.filter(status='moderation')
    internships = Internship.objects.filter(status='moderation')

    context = {
        'vacancies': vacancies,
        'internships': internships,
    }
    return render(request, 'career_app/moderation_list.html', context)


@login_required
@user_passes_test(is_admin)
def moderate_vacancy(request, pk, action):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if action == 'approve':
        vacancy.status = 'published'
        vacancy.save()
        messages.success(request, f'Вакансия "{vacancy.title}" опубликована!')
    elif action == 'reject':
        vacancy.status = 'rejected'
        vacancy.save()
        messages.success(request, f'Вакансия "{vacancy.title}" отклонена!')

    return redirect('moderation_list')


@login_required
@user_passes_test(is_admin)
def moderate_internship(request, pk, action):
    internship = get_object_or_404(Internship, pk=pk)

    if action == 'approve':
        internship.status = 'published'
        internship.save()
        messages.success(request, f'Стажировка "{internship.title}" опубликована!')
    elif action == 'reject':
        internship.status = 'rejected'
        internship.save()
        messages.success(request, f'Стажировка "{internship.title}" отклонена!')

    return redirect('moderation_list')


@login_required
@user_passes_test(is_admin)
def analytics(request):
    """Аналитика для администратора"""
    # Базовая аналитика
    vacancies_by_company = Vacancy.objects.filter(status='published').values(
        'company__name'
    ).annotate(count=Count('id')).order_by('-count')

    applications_by_vacancy = Application.objects.values(
        'vacancy__title'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    # Общая статистика
    total_vacancies = Vacancy.objects.count()
    total_internships = Internship.objects.count()
    total_applications = Application.objects.count()
    total_companies = Company.objects.count()

    context = {
        'vacancies_by_company': vacancies_by_company,
        'applications_by_vacancy': applications_by_vacancy,
        'total_vacancies': total_vacancies,
        'total_internships': total_internships,
        'total_applications': total_applications,
        'total_companies': total_companies,
    }
    return render(request, 'career_app/analytics.html', context)


@login_required
def create_applicant_profile(request):
    """Перенаправляем на общую настройку профиля"""
    # Устанавливаем роль соискателя если еще не установлена
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'applicant':
            user_profile.role = 'applicant'
            user_profile.save()
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='applicant')

    return redirect('profile_setup')


@login_required
def update_applicant_profile(request):
    """Перенаправляем на общую настройку профиля"""
    return redirect('profile_setup')


@login_required
def profile_setup(request):
    """Универсальная настройка профиля"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='applicant')

    # Если пользователь - соискатель, получаем или создаем его профиль
    applicant = None
    if user_profile.role == 'applicant':
        try:
            applicant = request.user.applicant
        except Applicant.DoesNotExist:
            applicant = Applicant.objects.create(
                user=request.user,
                first_name=request.user.first_name or '',
                last_name=request.user.last_name or '',
                email=request.user.email or ''
            )

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=user_profile)

        # Для соискателя также обрабатываем форму Applicant
        if user_profile.role == 'applicant':
            applicant_form = ApplicantForm(request.POST, request.FILES, instance=applicant)
            if user_profile_form.is_valid() and applicant_form.is_valid():
                user_profile_form.save()
                applicant_form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('dashboard')
        else:
            if user_profile_form.is_valid():
                user_profile_form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('dashboard')
    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        applicant_form = ApplicantForm(instance=applicant) if user_profile.role == 'applicant' else None

    context = {
        'user_profile_form': user_profile_form,
        'applicant_form': applicant_form,
    }
    return render(request, 'career_app/profile_setup.html', context)