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