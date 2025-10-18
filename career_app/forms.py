from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(
        choices=[
            ('applicant', 'Соискатель'),
            ('hr', 'HR компании'),
            ('university', 'Представитель вуза'),
            # Админ убран из выбора при регистрации
        ],
        label="Роль в системе",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label="Название компании",
        help_text="Заполните, если выбрали роль HR компании",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    institution_name = forms.CharField(
        max_length=200,
        required=False,
        label="Название учебного заведения",
        help_text="Заполните, если выбрали роль представителя вуза",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'company_name', 'institution_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company_name = cleaned_data.get('company_name')
        institution_name = cleaned_data.get('institution_name')

        if role == 'hr' and not company_name:
            raise forms.ValidationError("Для роли HR компании необходимо указать название компании")
        if role == 'university' and not institution_name:
            raise forms.ValidationError("Для роли представителя вуза необходимо указать название учебного заведения")

        return cleaned_data


class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = [
        ('applicant', 'Соискатель'),
        ('hr', 'HR компании'),
        ('university', 'Представитель вуза'),
        ('admin', 'Администратор ОЭЗ'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Выберите роль для входа",
        widget=forms.RadioSelect
    )


class CustomLoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


# Остальные формы остаются без изменений
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']
        # Убрали поле role из формы редактирования


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'email', 'phone', 'resume_file', 'resume_text']


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'category', 'description', 'requirements', 'salary', 'contact_info']


class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['title', 'category', 'specialty', 'student_count', 'period', 'description', 'requirements']


class InternshipResponseForm(forms.ModelForm):
    class Meta:
        model = InternshipResponse
        fields = ['cover_letter']


class AdminPromotionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Пользователь",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исключаем пользователей, которые уже админы
        admin_users = UserProfile.objects.filter(role='admin').values_list('user_id', flat=True)
        self.fields['user'].queryset = User.objects.exclude(id__in=admin_users)


# forms.py - добавить новые формы
class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'file']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите ваше сообщение...',
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'message': 'Сообщение',
            'file': 'Прикрепить файл'
        }

# Добавить в forms.py

class IdealCandidateProfileForm(forms.ModelForm):
    EXPERIENCE_LEVELS = [
        ('', '--- Выберите уровень ---'),
        ('junior', 'Junior (Начинающий)'),
        ('middle', 'Middle (Опытный)'),
        ('senior', 'Senior (Старший)'),
        ('lead', 'Lead (Руководитель)'),
    ]

    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVELS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Уровень опыта'
    )

    class Meta:
        model = IdealCandidateProfile
        fields = [
            'title', 'ideal_resume', 'required_skills', 'experience_level',
            'education_requirements', 'min_match_percentage', 'max_candidates'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Старший Python разработчик'}),
            'ideal_resume': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Опишите идеального кандидата: навыки, опыт, образование, личные качества...'
            }),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Python, Django, REST API, Docker, PostgreSQL, лидерство'
            }),
            'education_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Требования к образованию (необязательно)'
            }),
            'min_match_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '10',
                'max': '100',
                'value': '70'
            }),
            'max_candidates': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'value': '10'
            }),
        }
        labels = {
            'title': 'Название профиля',
            'ideal_resume': 'Идеальное резюме',
            'required_skills': 'Требуемые навыки',
            'education_requirements': 'Требования к образованию',
            'min_match_percentage': 'Минимальный процент совпадения (%)',
            'max_candidates': 'Количество кандидатов для поиска',
        }


class IdealVacancyProfileForm(forms.ModelForm):
    EXPERIENCE_LEVELS = [
        ('', '--- Выберите уровень ---'),
        ('intern', 'Стажер'),
        ('junior', 'Junior (Начинающий)'),
        ('middle', 'Middle (Опытный)'),
        ('senior', 'Senior (Старший)'),
        ('lead', 'Lead (Руководитель)'),
    ]

    EMPLOYMENT_TYPES = [
        ('', '--- Выберите тип ---'),
        ('full', 'Полная занятость'),
        ('part', 'Частичная занятость'),
        ('project', 'Проектная работа'),
        ('volunteer', 'Волонтерство'),
        ('internship', 'Стажировка'),
    ]

    WORK_SCHEDULES = [
        ('', '--- Выберите график ---'),
        ('full_day', 'Полный день'),
        ('flexible', 'Гибкий график'),
        ('remote', 'Удаленная работа'),
        ('shift', 'Сменный график'),
        ('rotation', 'Вахтовый метод'),
    ]

    # Поля для выбора категорий
    main_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_main=True),
        required=False,
        label="Основная категория",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_main_category'})
    )

    subcategory = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Подкатегория",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_subcategory'})
    )

    # Поле для выбора тегов
    selected_skill_tags = forms.ModelMultipleChoiceField(
        queryset=SkillTag.objects.none(),
        required=False,
        label="Выберите навыки (максимум 10)",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'skill-tags-checkbox'}),
        help_text="Выберите до 10 наиболее важных для вас навыков"
    )

    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVELS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Уровень опыта'
    )

    education_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(),
        required=False,
        label="Уровень образования",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    employment_types = forms.MultipleChoiceField(
        choices=EMPLOYMENT_TYPES[1:],  # исключаем пустой выбор
        required=False,
        label="Тип занятости",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'employment-checkbox'}),
        help_text="Можно выбрать несколько вариантов"
    )

    work_schedule = forms.MultipleChoiceField(
        choices=WORK_SCHEDULES[1:],  # исключаем пустой выбор
        required=False,
        label="График работы",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'schedule-checkbox'}),
        help_text="Можно выбрать несколько вариантов"
    )

    class Meta:
        model = IdealVacancyProfile
        fields = [
            'title', 'main_category', 'subcategory', 'ideal_position',
            'selected_skill_tags', 'experience_level', 'education_level',
            'desired_salary', 'location_preferences', 'employment_types',
            'work_schedule', 'min_match_percentage', 'max_vacancies'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Удаленная работа Python разработчиком'
            }),
            'ideal_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Желаемая должность'
            }),
            'desired_salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример: от 100000 руб.'
            }),
            'location_preferences': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример: Москва, удаленно, гибридный формат'
            }),
            'min_match_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '10',
                'max': '100',
                'value': '70'
            }),
            'max_vacancies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'value': '10'
            }),
        }
        labels = {
            'title': 'Название профиля',
            'ideal_position': 'Идеальная должность',
            'desired_salary': 'Желаемая зарплата',
            'location_preferences': 'Предпочтения по локации',
            'min_match_percentage': 'Минимальный процент совпадения (%)',
            'max_vacancies': 'Количество вакансий для поиска',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если есть instance, заполняем поля
        if self.instance and self.instance.pk:
            if self.instance.subcategory:
                self.fields['main_category'].initial = self.instance.subcategory.parent
                self.fields['subcategory'].queryset = Category.objects.filter(
                    parent=self.instance.subcategory.parent
                )

            if self.instance.selected_skill_tags.exists():
                self.fields['selected_skill_tags'].queryset = SkillTag.objects.filter(
                    category=self.instance.subcategory
                )
            else:
                self.fields['selected_skill_tags'].queryset = SkillTag.objects.none()
        else:
            self.fields['subcategory'].queryset = Category.objects.none()
            self.fields['selected_skill_tags'].queryset = SkillTag.objects.none()

    def clean_selected_skill_tags(self):
        tags = self.cleaned_data.get('selected_skill_tags')
        if tags and len(tags) > 10:
            raise forms.ValidationError("Можно выбрать не более 10 навыков")
        return tags

    def clean(self):
        cleaned_data = super().clean()
        main_category = cleaned_data.get('main_category')
        subcategory = cleaned_data.get('subcategory')

        if subcategory and main_category:
            if subcategory.parent != main_category:
                raise forms.ValidationError("Выбранная подкатегория не принадлежит выбранной основной категории")

        return cleaned_data


class ApplicantResumeForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'position', 'experience', 'education', 'skills', 'about',
            'resume_file', 'resume_text', 'is_published'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример: Python разработчик, Маркетолог, Менеджер проектов'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите ваш опыт работы: компании, должности, проекты, достижения...'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваше образование: вузы, курсы, сертификаты...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ключевые навыки: Python, Django, английский язык, управление проектами...'
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Расскажите о себе, ваших целях, интересах...'
            }),
            'resume_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Или просто вставьте полный текст вашего резюме здесь...'
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_published': 'Разрешить компаниям находить мое резюме в поиске',
        }