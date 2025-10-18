from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


# Добавим новую модель для запросов на подтверждение роли
class RoleApprovalRequest(models.Model):
    ROLE_CHOICES = [
        ('hr', 'HR компании'),
        ('university', 'Представитель вуза'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    requested_role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Запрашиваемая роль")
    company_name = models.CharField(max_length=200, blank=True, verbose_name="Название компании")
    institution_name = models.CharField(max_length=200, blank=True, verbose_name="Название учебного заведения")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ], default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_requests', verbose_name="Рассмотрено")

    class Meta:
        verbose_name = "Запрос на подтверждение роли"
        verbose_name_plural = "Запросы на подтверждение роли"

    def __str__(self):
        return f"{self.user.username} - {self.get_requested_role_display()}"


class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название компании")
    description = models.TextField(verbose_name="Описание")
    contact_email = models.EmailField(verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, verbose_name="Подтверждена")  # Новое поле

    objects = models.Manager()

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name


class EducationalInstitution(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название учебного заведения")
    contact_email = models.EmailField(verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, verbose_name="Подтверждено")  # Новое поле

    objects = models.Manager()

    class Meta:
        verbose_name = "Учебное заведение"
        verbose_name_plural = "Учебные заведения"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Родительская категория")
    is_main = models.BooleanField(default=False, verbose_name="Основная категория")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['is_main', 'name']

    def __str__(self):
        return self.name

    def get_subcategories(self):
        """Возвращает все подкатегории"""
        return Category.objects.filter(parent=self)

    def is_subcategory(self):
        """Проверяет, является ли категория подкатегорией"""
        return self.parent is not None


class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликована'),
        ('rejected', 'Отклонена'),
        ('closed', 'Закрыта'),
    ]

    title = models.CharField(max_length=200, verbose_name="Должность")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    description = models.TextField(verbose_name="Описание вакансии")
    requirements = models.TextField(verbose_name="Требования")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата")
    contact_info = models.TextField(verbose_name="Контактная информация")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    auto_close_at = models.DateTimeField(null=True, blank=True, verbose_name="Автоматическое закрытие")

    objects = models.Manager()

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('vacancy_detail', kwargs={'pk': self.pk})


class Internship(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликована'),
        ('rejected', 'Отклонена'),
        ('closed', 'Закрыта'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название стажировки")
    institution = models.ForeignKey(EducationalInstitution, on_delete=models.CASCADE, verbose_name="Учебное заведение")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    specialty = models.CharField(max_length=200, verbose_name="Специальность")
    student_count = models.IntegerField(verbose_name="Количество студентов")
    period = models.CharField(max_length=100, verbose_name="Период стажировки")
    description = models.TextField(verbose_name="Описание")
    requirements = models.TextField(verbose_name="Требования к студентам")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Стажировка"
        verbose_name_plural = "Стажировки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.institution.name}"


class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True, verbose_name="Файл резюме")
    resume_text = models.TextField(blank=True, verbose_name="Текст резюме")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Соискатель"
        verbose_name_plural = "Соискатели"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('reviewed', 'Рассмотрена'),
        ('invited', 'Приглашен'),
        ('rejected', 'Отклонена'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, verbose_name="Вакансия")
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, verbose_name="Соискатель")
    cover_letter = models.TextField(blank=True, verbose_name="Сопроводительное письмо")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    applied_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant} - {self.vacancy.title}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор ОЭЗ'),
        ('hr', 'HR компании'),
        ('university', 'Представитель вуза'),
        ('applicant', 'Соискатель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Роль")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Компания")
    institution = models.ForeignKey(EducationalInstitution, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Учебное заведение")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    is_approved = models.BooleanField(default=False, verbose_name="Подтвержден")

    objects = models.Manager()

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def can_access_dashboard(self):
        """Проверяет, может ли пользователь получить доступ к дашборду"""
        # Админы всегда имеют доступ
        if self.role == 'admin':
            return True
        # Соискатели всегда имеют доступ
        if self.role == 'applicant':
            return True
        # HR и университеты требуют подтверждения
        return self.is_approved

    def save(self, *args, **kwargs):
        # Админы автоматически подтверждаются
        if self.role == 'admin':
            self.is_approved = True
        super().save(*args, **kwargs)


class InternshipApplication(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('reviewed', 'Рассмотрена'),
        ('invited', 'Приглашены'),
        ('rejected', 'Отклонена'),
    ]

    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, verbose_name="Стажировка")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    contact_person = models.CharField(max_length=200, verbose_name="Контактное лицо")
    contact_email = models.EmailField(verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    proposal = models.TextField(verbose_name="Предложение по стажировке")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отклик на стажировку"
        verbose_name_plural = "Отклики на стажировки"
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.company.name} - {self.internship.title}"


class InternshipResponse(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('reviewed', 'Рассмотрена'),
        ('invited', 'Приглашен'),
        ('rejected', 'Отклонена'),
    ]

    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, verbose_name="Стажировка")
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, verbose_name="Соискатель")
    cover_letter = models.TextField(verbose_name="Сопроводительное письмо")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отклик на стажировку"
        verbose_name_plural = "Отклики на стажировки"
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant} - {self.internship.title}"