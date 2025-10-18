from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import *
from .forms import *
from django.conf import settings


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Получаем или создаем профиль пользователя
            role = form.cleaned_data['role']

            try:
                # Пытаемся получить существующий профиль
                user_profile = user.userprofile
                # Обновляем роль
                user_profile.role = role
                user_profile.save()
            except UserProfile.DoesNotExist:
                # Создаем новый профиль если не существует
                user_profile = UserProfile.objects.create(user=user, role=role)

            # Для HR и университетов создаем запрос на подтверждение
            if role in ['hr', 'university']:
                company_name = form.cleaned_data.get('company_name', '')
                institution_name = form.cleaned_data.get('institution_name', '')

                RoleApprovalRequest.objects.create(
                    user=user,
                    requested_role=role,
                    company_name=company_name,
                    institution_name=institution_name
                )

                # Создаем компанию или учебное заведение
                if role == 'hr' and company_name:
                    company = Company.objects.create(
                        name=company_name,
                        contact_email=user.email,
                        contact_phone='',
                        is_approved=False
                    )
                    user_profile.company = company
                    user_profile.save()

                elif role == 'university' and institution_name:
                    institution = EducationalInstitution.objects.create(
                        name=institution_name,
                        contact_email=user.email,
                        contact_phone='',
                        is_approved=False
                    )
                    user_profile.institution = institution
                    user_profile.save()

                messages.success(request,
                                 'Регистрация прошла успешно! Ваш аккаунт ожидает подтверждения администратором.')
                return redirect('pending_approval')

            else:  # Для соискателей
                # Создаем или обновляем профиль соискателя
                applicant, created = Applicant.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'email': user.email or ''
                    }
                )

                # Соискатели автоматически подтверждаются
                user_profile.is_approved = True
                user_profile.save()

                login(request, user)
                messages.success(request, 'Регистрация прошла успешно! Заполните ваш профиль.')
                return redirect('profile_setup')

    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def is_admin(user):
    try:
        return user.userprofile.role == 'admin'  # Админы не требуют is_approved
    except UserProfile.DoesNotExist:
        return False

def is_hr(user):
    try:
        return user.userprofile.role == 'hr' and user.userprofile.is_approved
    except UserProfile.DoesNotExist:
        return False

def is_university(user):
    try:
        return user.userprofile.role == 'university' and user.userprofile.is_approved
    except UserProfile.DoesNotExist:
        return False


def home(request):
    try:
        vacancies = Vacancy.objects.filter(status='published')[:3]
        internships = Internship.objects.filter(status='published')[:3]

        # Создаем объединенный список для главной страницы
        recent_items = []

        for vacancy in vacancies:
            recent_items.append({
                'type': 'vacancy',
                'id': vacancy.id,
                'title': vacancy.title,
                'company': vacancy.company.name,
                'description': vacancy.description,
                'salary': vacancy.salary,
            })

        for internship in internships:
            recent_items.append({
                'type': 'internship',
                'id': internship.id,
                'title': internship.title,
                'company': internship.institution.name,
                'description': internship.description,
            })

        # Сортируем по дате (можно добавить дату создания)
        recent_items.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    except Exception as e:
        recent_items = []
        if settings.DEBUG:
            messages.info(request, f'Отладочная информация: {e}')

    context = {
        'recent_items': recent_items,
        'debug': settings.DEBUG,
    }
    return render(request, 'career_app/home.html', context)


def vacancy_list(request):
    # Получаем все опубликованные вакансии и стажировки
    vacancies = Vacancy.objects.filter(status='published')
    internships = Internship.objects.filter(status='published')

    # Параметры фильтрации из GET-запроса
    filter_type = request.GET.get('type', 'all')
    selected_categories = request.GET.getlist('category')  # Множественный выбор
    selected_main_categories = request.GET.getlist('main_category')  # Множественный выбор

    # Объединяем данные в один список с пометкой типа
    items = []

    # Добавляем вакансии
    for vacancy in vacancies:
        items.append({
            'type': 'vacancy',
            'object': vacancy,
            'title': vacancy.title,
            'company': vacancy.company.name,
            'description': vacancy.description,
            'salary': vacancy.salary,
            'category': vacancy.category,
            'created_at': vacancy.created_at,
            'id': vacancy.id,
        })

    # Добавляем стажировки
    for internship in internships:
        items.append({
            'type': 'internship',
            'object': internship,
            'title': internship.title,
            'company': internship.institution.name,
            'description': internship.description,
            'specialty': internship.specialty,
            'student_count': internship.student_count,
            'period': internship.period,
            'category': internship.category,
            'created_at': internship.created_at,
            'id': internship.id,
        })

    # Применяем фильтры
    if filter_type == 'vacancies':
        items = [item for item in items if item['type'] == 'vacancy']
    elif filter_type == 'internships':
        items = [item for item in items if item['type'] == 'internship']

    # Фильтр по основным категориям
    if selected_main_categories:
        main_category_ids = [int(cat_id) for cat_id in selected_main_categories]
        main_categories = Category.objects.filter(id__in=main_category_ids)
        subcategory_ids = []
        for main_cat in main_categories:
            subcategory_ids.extend([subcat.id for subcat in main_cat.get_subcategories()])
        items = [item for item in items if item['category'] and item['category'].id in subcategory_ids]

    # Фильтр по конкретным категориям
    if selected_categories and not selected_main_categories:
        category_ids = [int(cat_id) for cat_id in selected_categories]
        items = [item for item in items if item['category'] and item['category'].id in category_ids]

    # Поиск
    query = request.GET.get('q')
    if query:
        items = [item for item in items if
                 query.lower() in item['title'].lower() or
                 query.lower() in item['description'].lower() or
                 query.lower() in item['company'].lower()]

    # Сортировка по дате создания (новые сначала)
    items.sort(key=lambda x: x['created_at'], reverse=True)

    # Пагинация
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем категории для фильтра
    main_categories = Category.objects.filter(is_main=True)
    all_categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'filter_type': filter_type,
        'selected_categories': [int(cat_id) for cat_id in selected_categories],
        'selected_main_categories': [int(cat_id) for cat_id in selected_main_categories],
        'main_categories': main_categories,
        'all_categories': all_categories,
        'total_count': len(items),
        'vacancies_count': len([item for item in items if item['type'] == 'vacancy']),
        'internships_count': len([item for item in items if item['type'] == 'internship']),
    }
    return render(request, 'career_app/vacancy_list.html', context)


def vacancy_detail(request, pk):
    try:
        vacancy = Vacancy.objects.get(pk=pk, status='published')
    except Vacancy.DoesNotExist:
        vacancy = get_object_or_404(Vacancy, pk=pk)
        can_view = False
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'hr':
                if vacancy.company == request.user.userprofile.company:
                    can_view = True
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
                can_view = True
        if not can_view:
            messages.error(request, 'У вас нет прав для просмотра этой вакансии или она еще не опубликована.')
            return redirect('vacancy_list')

    # Инициализируем переменные
    has_applied = False
    chat_thread = None
    applicant = None
    show_chat_button = False

    # Проверяем для авторизованных пользователей-соискателей
    if request.user.is_authenticated and hasattr(request.user,
                                                 'userprofile') and request.user.userprofile.role == 'applicant':
        try:
            applicant = request.user.applicant
            # Проверяем, откликался ли уже пользователь
            has_applied = Application.objects.filter(
                vacancy=vacancy,
                applicant=applicant
            ).exists()

            # Ищем существующий чат
            if has_applied:
                chat_thread = ChatThread.objects.filter(
                    vacancy=vacancy,
                    applicant=applicant,
                    is_active=True
                ).first()
                if chat_thread:
                    show_chat_button = True

        except Applicant.DoesNotExist:
            pass

    # Обработка POST запроса (отклик)
    if request.method == 'POST' and vacancy.status == 'published':
        if not request.user.is_authenticated:
            # Обработка для неавторизованных пользователей
            applicant_form = ApplicantForm(request.POST, request.FILES)
            if applicant_form.is_valid():
                applicant = applicant_form.save()
                application = Application.objects.create(
                    vacancy=vacancy,
                    applicant=applicant,
                    cover_letter=request.POST.get('cover_letter', '')
                )

                # Создаем чат сразу
                if vacancy.company and vacancy.company.userprofile_set.filter(role='hr').exists():
                    hr_user = vacancy.company.userprofile_set.filter(role='hr').first().user
                    chat_thread, created = ChatThread.get_or_create_chat(
                        vacancy=vacancy,
                        applicant=applicant,
                        hr_user=hr_user
                    )
                    if created:
                        ChatMessage.objects.create(
                            thread=chat_thread,
                            sender=applicant.user if applicant.user else None,
                            message=request.POST.get('cover_letter',
                                                     '') or "Здравствуйте! Я откликнулся на вашу вакансию."
                        )

                # Обновляем переменные для отображения
                has_applied = True
                show_chat_button = True
                messages.success(request, 'Ваш отклик успешно отправлен! Чат создан.')

        else:
            # Обработка для авторизованных пользователей
            if request.user.userprofile.role == 'applicant':
                try:
                    applicant = request.user.applicant

                    if not has_applied:
                        # Создаем отклик
                        application = Application.objects.create(
                            vacancy=vacancy,
                            applicant=applicant,
                            cover_letter=request.POST.get('cover_letter', '')
                        )

                        # Создаем чат сразу
                        if vacancy.company and vacancy.company.userprofile_set.filter(role='hr').exists():
                            hr_user = vacancy.company.userprofile_set.filter(role='hr').first().user
                            chat_thread, created = ChatThread.get_or_create_chat(
                                vacancy=vacancy,
                                applicant=applicant,
                                hr_user=hr_user
                            )
                            if created:
                                ChatMessage.objects.create(
                                    thread=chat_thread,
                                    sender=request.user,
                                    message=request.POST.get('cover_letter',
                                                             '') or "Здравствуйте! Я откликнулся на вашу вакансию."
                                )

                        # Обновляем переменные для отображения
                        has_applied = True
                        show_chat_button = True
                        messages.success(request, 'Ваш отклик успешно отправлен! Чат создан.')
                    else:
                        messages.info(request, 'Вы уже откликались на эту вакансию.')

                except Applicant.DoesNotExist:
                    messages.error(request, 'Пожалуйста, заполните ваш профиль соискателя.')
                    return redirect('create_applicant_profile')
            else:
                messages.error(request, 'Откликаться на вакансии могут только соискатели.')

    # Форма для неавторизованных пользователей
    applicant_form = ApplicantForm()

    context = {
        'vacancy': vacancy,
        'applicant_form': applicant_form,
        'has_applied': has_applied,
        'chat_thread': chat_thread,
        'show_chat_button': show_chat_button,
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


def internship_detail(request, pk):
    try:
        internship = get_object_or_404(Internship, pk=pk, status='published')
    except Internship.DoesNotExist:
        messages.error(request, 'Стажировка не найдена или еще не опубликована.')
        return redirect('vacancy_list')

    # Инициализируем переменные
    has_applied = False
    chat_thread = None
    applicant = None
    show_chat_button = False

    # Проверяем для авторизованных пользователей-соискателей
    if request.user.is_authenticated and hasattr(request.user,
                                                 'userprofile') and request.user.userprofile.role == 'applicant':
        try:
            applicant = request.user.applicant
            # Проверяем, откликался ли уже пользователь
            has_applied = InternshipResponse.objects.filter(
                internship=internship,
                applicant=applicant
            ).exists()

            # Ищем существующий чат
            if has_applied:
                chat_thread = ChatThread.objects.filter(
                    internship=internship,
                    applicant=applicant,
                    is_active=True
                ).first()
                if chat_thread:
                    show_chat_button = True

        except Applicant.DoesNotExist:
            pass

    # Обработка POST запроса (отклик)
    if request.method == 'POST' and internship.status == 'published':
        if request.user.is_authenticated and request.user.userprofile.role == 'applicant':
            try:
                applicant = request.user.applicant

                if not has_applied:
                    # Создаем отклик
                    response = InternshipResponse.objects.create(
                        internship=internship,
                        applicant=applicant,
                        cover_letter=request.POST.get('cover_letter', '')
                    )

                    # Создаем чат сразу
                    if internship.institution and internship.institution.userprofile_set.filter(
                            role='university').exists():
                        university_user = internship.institution.userprofile_set.filter(role='university').first().user
                        chat_thread, created = ChatThread.get_or_create_chat(
                            internship=internship,
                            applicant=applicant,
                            university_user=university_user
                        )
                        if created:
                            ChatMessage.objects.create(
                                thread=chat_thread,
                                sender=request.user,
                                message=request.POST.get('cover_letter',
                                                         '') or "Здравствуйте! Я откликнулся на вашу стажировку."
                            )

                    # Обновляем переменные для отображения
                    has_applied = True
                    show_chat_button = True
                    messages.success(request, 'Ваш отклик на стажировку успешно отправлен! Чат создан.')
                else:
                    messages.info(request, 'Вы уже откликались на эту стажировку.')

            except Applicant.DoesNotExist:
                messages.error(request, 'Пожалуйста, заполните ваш профиль соискателя.')
                return redirect('create_applicant_profile')
        else:
            messages.error(request, 'Для отклика на стажировку необходимо войти в систему как соискатель.')

    form = InternshipResponseForm()

    context = {
        'internship': internship,
        'form': form,
        'has_applied': has_applied,
        'chat_thread': chat_thread,
        'show_chat_button': show_chat_button,
        'applicant': applicant,
    }
    return render(request, 'career_app/internship_detail.html', context)

@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.info(request, "Пожалуйста, завершите настройку вашего профиля.")
        return redirect('profile_setup')

    # Проверяем доступ к дашборду
    if not user_profile.can_access_dashboard():
        messages.warning(request, "Ваш аккаунт ожидает подтверждения администратором.")
        return redirect('pending_approval')

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

    # Получаем отклики на стажировки
    internship_responses = InternshipResponse.objects.filter(
        internship__institution=institution
    ).select_related('applicant', 'internship').order_by('-applied_at')

    # Статистика
    internships_published = internships.filter(status='published').count()
    internships_moderation = internships.filter(status='moderation').count()
    total_responses = internship_responses.count()

    context = {
        'institution': institution,
        'internships': internships,
        'internship_responses': internship_responses,
        'internships_published': internships_published,
        'internships_moderation': internships_moderation,
        'total_responses': total_responses,
    }
    return render(request, 'career_app/university_dashboard.html', context)


@login_required
def applicant_dashboard(request):
    try:
        applicant = request.user.applicant
        applications = Application.objects.filter(applicant=applicant)
        internship_responses = InternshipResponse.objects.filter(applicant=applicant)
    except Applicant.DoesNotExist:
        applicant = None
        applications = []
        internship_responses = []

    context = {
        'applicant': applicant,
        'applications': applications,
        'internship_responses': internship_responses,
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


def role_selection(request):
    """Первая страница - выбор роли для входа"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            request.session['selected_role'] = form.cleaned_data['role']
            return redirect('custom_login')
    else:
        form = RoleSelectionForm()

    context = {
        'form': form,
        'role_choices': [
            ('applicant', 'Соискатель'),
            ('hr', 'HR компании'),
            ('university', 'Представитель вуза'),
            ('admin', 'Администратор ОЭЗ'),
        ]
    }
    return render(request, 'career_app/role_selection.html', context)


def custom_login(request):
    """Вторая страница - ввод логина и пароля"""
    selected_role = request.session.get('selected_role')

    if not selected_role:
        return redirect('role_selection')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    user_profile = user.userprofile
                    if user_profile.role != selected_role:
                        messages.error(request,
                                       f'Выбранная роль не соответствует вашему профилю. Ваша роль: {user_profile.get_role_display()}')
                        return redirect('role_selection')

                    # Для HR и университетов проверяем подтверждение
                    if user_profile.role in ['hr', 'university'] and not user_profile.is_approved:
                        messages.warning(request, 'Ваш аккаунт ожидает подтверждения администратором.')
                        return redirect('pending_approval')

                    login(request, user)
                    return redirect('dashboard')

                except UserProfile.DoesNotExist:
                    messages.error(request, 'Профиль пользователя не найден.')
                    return redirect('role_selection')
            else:
                messages.error(request, 'Неверный логин или пароль.')
    else:
        form = CustomLoginForm()

    role_display = dict(RoleSelectionForm.ROLE_CHOICES).get(selected_role, selected_role)

    context = {
        'form': form,
        'selected_role': selected_role,
        'role_display': role_display,
    }
    return render(request, 'career_app/custom_login.html', context)

def pending_approval(request):
    """Страница ожидания подтверждения"""
    return render(request, 'career_app/pending_approval.html')

@login_required
@user_passes_test(is_admin)
def admin_promotion(request):
    """Назначение новых администраторов"""
    if request.method == 'POST':
        form = AdminPromotionForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            try:
                user_profile = user.userprofile
                # Меняем роль на админа
                user_profile.role = 'admin'
                user_profile.is_approved = True  # Админы автоматически подтверждаются
                user_profile.save()

                messages.success(request, f'Пользователь {user.username} теперь администратор!')
                return redirect('admin_promotion')

            except UserProfile.DoesNotExist:
                # Создаем новый профиль с ролью админа
                UserProfile.objects.create(
                    user=user,
                    role='admin',
                    is_approved=True
                )
                messages.success(request, f'Пользователь {user.username} теперь администратор!')
                return redirect('admin_promotion')
    else:
        form = AdminPromotionForm()

    # Список текущих администраторов
    current_admins = UserProfile.objects.filter(role='admin').select_related('user')

    context = {
        'form': form,
        'current_admins': current_admins,
    }
    return render(request, 'career_app/admin_promotion.html', context)


@login_required
@user_passes_test(is_admin)
def revoke_admin(request, user_id):
    """Отзыв прав администратора"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # Не позволяем отозвать права у самого себя
        if user == request.user:
            messages.error(request, 'Вы не можете отозвать права администратора у самого себя!')
            return redirect('admin_promotion')

        try:
            user_profile = user.userprofile
            # Меняем роль на соискателя (или другую базовую роль)
            user_profile.role = 'applicant'
            user_profile.save()

            messages.success(request, f'Права администратора отозваны у пользователя {user.username}')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Профиль пользователя не найден')

    return redirect('admin_promotion')


@login_required
@user_passes_test(is_admin)
def role_approval_list(request):
    """Список запросов на подтверждение ролей HR и университетов"""
    pending_requests = RoleApprovalRequest.objects.filter(status='pending').select_related('user')
    approved_requests = RoleApprovalRequest.objects.filter(status='approved').select_related('user')[
                        :10]  # Последние 10
    rejected_requests = RoleApprovalRequest.objects.filter(status='rejected').select_related('user')[
                        :10]  # Последние 10

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'career_app/role_approval_list.html', context)


@login_required
@user_passes_test(is_admin)
def approve_role(request, request_id, action):
    """Подтверждение или отклонение роли"""
    role_request = get_object_or_404(RoleApprovalRequest, id=request_id)

    if action == 'approve':
        role_request.status = 'approved'
        role_request.reviewed_at = timezone.now()
        role_request.reviewed_by = request.user

        # Обновляем профиль пользователя
        user_profile = role_request.user.userprofile
        user_profile.is_approved = True
        user_profile.save()

        # Подтверждаем компанию или учебное заведение
        if role_request.requested_role == 'hr' and user_profile.company:
            user_profile.company.is_approved = True
            user_profile.company.save()
        elif role_request.requested_role == 'university' and user_profile.institution:
            user_profile.institution.is_approved = True
            user_profile.institution.save()

        messages.success(request, f'Роль для пользователя {role_request.user.username} подтверждена!')

    elif action == 'reject':
        role_request.status = 'rejected'
        role_request.reviewed_at = timezone.now()
        role_request.reviewed_by = request.user

        # Можно также отправить уведомление пользователю
        messages.success(request, f'Запрос роли для пользователя {role_request.user.username} отклонен!')

    role_request.save()
    return redirect('role_approval_list')


# views.py - добавить новые представления
@login_required
def chat_list(request):
    """Список чатов пользователя"""
    user_profile = request.user.userprofile

    if user_profile.role == 'applicant':
        # Для соискателя - чаты с HR и университетами
        threads = ChatThread.objects.filter(
            applicant__user=request.user,
            is_active=True
        ).select_related('vacancy', 'internship', 'hr_user', 'university_user')

    elif user_profile.role == 'hr':
        # Для HR - чаты по вакансиям его компании
        threads = ChatThread.objects.filter(
            vacancy__company=user_profile.company,
            is_active=True
        ).select_related('vacancy', 'applicant', 'hr_user')

    elif user_profile.role == 'university':
        # Для университета - чаты по стажировкам его учреждения
        threads = ChatThread.objects.filter(
            internship__institution=user_profile.institution,
            is_active=True
        ).select_related('internship', 'applicant', 'university_user')

    else:
        threads = ChatThread.objects.none()

    # Помечаем непрочитанные сообщения
    for thread in threads:
        thread.unread_count = thread.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()

    context = {
        'threads': threads,
    }
    return render(request, 'career_app/chat_list.html', context)


@login_required
def chat_detail(request, thread_id):
    """Детальная страница чата"""
    thread = get_object_or_404(ChatThread, id=thread_id)

    # Проверка прав доступа к чату
    user_profile = request.user.userprofile
    has_access = False

    if user_profile.role == 'applicant':
        has_access = thread.applicant.user == request.user
    elif user_profile.role == 'hr':
        has_access = thread.vacancy and thread.vacancy.company == user_profile.company
    elif user_profile.role == 'university':
        has_access = thread.internship and thread.internship.institution == user_profile.institution
    elif user_profile.role == 'admin':
        has_access = True

    if not has_access:
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('chat_list')

    # Помечаем сообщения как прочитанные
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()

            # Обновляем время последней активности чата
            thread.save()

            return redirect('chat_detail', thread_id=thread_id)
    else:
        form = ChatMessageForm()

    messages_list = thread.messages.all().select_related('sender')

    context = {
        'thread': thread,
        'messages_list': messages_list,
        'form': form,
        'other_user': thread.get_other_participant(request.user),
    }
    return render(request, 'career_app/chat_detail.html', context)


@login_required
def create_chat_from_application(request, application_id):
    """Создание чата из отклика на вакансию"""
    application = get_object_or_404(Application, id=application_id)

    # Проверяем, что пользователь - HR компании вакансии
    if not (request.user.userprofile.role == 'hr' and
            application.vacancy.company == request.user.userprofile.company):
        messages.error(request, 'У вас нет прав для создания чата.')
        return redirect('hr_dashboard')

    # Создаем или получаем существующий чат
    thread, created = ChatThread.objects.get_or_create(
        vacancy=application.vacancy,
        applicant=application.applicant,
        hr_user=request.user,
        defaults={'is_active': True}
    )

    if created:
        # Создаем первое сообщение от HR
        ChatMessage.objects.create(
            thread=thread,
            sender=request.user,
            message=f"Здравствуйте! Благодарим за отклик на вакансию '{application.vacancy.title}'. Давайте обсудим вашу кандидатуру."
        )
        messages.success(request, 'Чат создан!')

    return redirect('chat_detail', thread_id=thread.id)


@login_required
def create_chat_from_internship_response(request, response_id):
    """Создание чата из отклика на стажировку"""
    response = get_object_or_404(InternshipResponse, id=response_id)

    # Проверяем, что пользователь - представитель университета
    if not (request.user.userprofile.role == 'university' and
            response.internship.institution == request.user.userprofile.institution):
        messages.error(request, 'У вас нет прав для создания чата.')
        return redirect('university_dashboard')

    # Создаем или получаем существующий чат
    thread, created = ChatThread.objects.get_or_create(
        internship=response.internship,
        applicant=response.applicant,
        university_user=request.user,
        defaults={'is_active': True}
    )

    if created:
        # Создаем первое сообщение от университета
        ChatMessage.objects.create(
            thread=thread,
            sender=request.user,
            message=f"Здравствуйте! Благодарим за интерес к стажировке '{response.internship.title}'. Давайте обсудим детали."
        )
        messages.success(request, 'Чат создан!')

    return redirect('chat_detail', thread_id=thread.id)