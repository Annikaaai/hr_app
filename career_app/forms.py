from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vacancy, Internship, Applicant, Application, UserProfile, Company, EducationalInstitution, \
    InternshipApplication, InternshipResponse


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'company', 'institution', 'phone']


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'category', 'description', 'requirements', 'salary', 'contact_info', 'auto_close_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'contact_info': forms.Textarea(attrs={'rows': 3}),
            'auto_close_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['title', 'category', 'specialty', 'student_count', 'period', 'description', 'requirements']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'email', 'phone', 'resume_file', 'resume_text']
        widgets = {
            'resume_text': forms.Textarea(attrs={'rows': 6}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'contact_email', 'contact_phone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class EducationalInstitutionForm(forms.ModelForm):
    class Meta:
        model = EducationalInstitution
        fields = ['name', 'contact_email', 'contact_phone']

class InternshipApplicationForm(forms.ModelForm):
    class Meta:
        model = InternshipApplication
        fields = ['contact_person', 'contact_email', 'contact_phone', 'proposal']
        widgets = {
            'proposal': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваше предложение по организации стажировки...'}),
        }

class InternshipResponseForm(forms.ModelForm):
    class Meta:
        model = InternshipResponse
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Расскажите почему вы хотите пройти эту стажировку и чем вы полезны...'
            }),
        }