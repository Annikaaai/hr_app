import os
import django
import sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techno_work.settings')
django.setup()

from career_app.models import Category


def create_categories():
    categories = [
        # IT и технологии
        {'name': 'Программист', 'description': 'Разработка программного обеспечения'},
        {'name': 'Веб-разработчик', 'description': 'Создание веб-сайтов и приложений'},
        {'name': 'Мобильный разработчик', 'description': 'Разработка мобильных приложений'},
        {'name': 'Data Scientist', 'description': 'Анализ данных и машинное обучение'},
        {'name': 'DevOps', 'description': 'Администрирование и автоматизация'},
        {'name': 'Тестировщик (QA)', 'description': 'Тестирование программного обеспечения'},
        {'name': 'Системный администратор', 'description': 'Обслуживание IT-инфраструктуры'},
        {'name': 'Аналитик данных', 'description': 'Анализ и визуализация данных'},

        # Дизайн и творчество
        {'name': 'Веб-дизайнер', 'description': 'Дизайн интерфейсов и сайтов'},
        {'name': 'Графический дизайнер', 'description': 'Создание графики и иллюстраций'},
        {'name': 'UI/UX дизайнер', 'description': 'Дизайн пользовательских интерфейсов'},
        {'name': '3D-дизайнер', 'description': 'Трехмерное моделирование и визуализация'},

        # Маркетинг и продажи
        {'name': 'Маркетолог', 'description': 'Продвижение товаров и услуг'},
        {'name': 'SMM-специалист', 'description': 'Продвижение в социальных сетях'},
        {'name': 'Копирайтер', 'description': 'Написание текстов и контента'},
        {'name': 'Продавец', 'description': 'Продажа товаров и услуг'},
        {'name': 'Менеджер по продажам', 'description': 'Управление продажами'},
        {'name': 'Торговый представитель', 'description': 'Работа с клиентами и партнерами'},

        # Менеджмент
        {'name': 'Проектный менеджер', 'description': 'Управление проектами'},
        {'name': 'Продуктовый менеджер', 'description': 'Управление продуктом'},
        {'name': 'Офис-менеджер', 'description': 'Административная работа'},
        {'name': 'HR-менеджер', 'description': 'Подбор и управление персоналом'},

        # Финансы и бухгалтерия
        {'name': 'Бухгалтер', 'description': 'Ведение бухгалтерского учета'},
        {'name': 'Финансовый аналитик', 'description': 'Анализ финансовых показателей'},
        {'name': 'Экономист', 'description': 'Экономический анализ и планирование'},

        # Образование и наука
        {'name': 'Преподаватель', 'description': 'Обучение и преподавание'},
        {'name': 'Ученый', 'description': 'Научные исследования'},
        {'name': 'Лаборант', 'description': 'Работа в лаборатории'},

        # Медицина и здоровье
        {'name': 'Врач', 'description': 'Медицинская практика'},
        {'name': 'Медсестра/медбрат', 'description': 'Медицинский уход'},
        {'name': 'Фармацевт', 'description': 'Работа в аптеке'},

        # Транспорт и логистика
        {'name': 'Водитель', 'description': 'Управление транспортными средствами'},
        {'name': 'Логист', 'description': 'Организация перевозок'},
        {'name': 'Курьер', 'description': 'Доставка товаров'},

        # Производство и строительство
        {'name': 'Инженер', 'description': 'Инженерные работы'},
        {'name': 'Техник', 'description': 'Техническое обслуживание'},
        {'name': 'Строитель', 'description': 'Строительные работы'},
        {'name': 'Архитектор', 'description': 'Проектирование зданий'},

        # Сфера услуг
        {'name': 'Повар', 'description': 'Приготовление пищи'},
        {'name': 'Официант', 'description': 'Обслуживание в ресторане'},
        {'name': 'Бариста', 'description': 'Приготовление кофе'},
        {'name': 'Администратор', 'description': 'Административная работа'},

        # Другие
        {'name': 'Юрист', 'description': 'Юридические услуги'},
        {'name': 'Переводчик', 'description': 'Перевод текстов'},
        {'name': 'Журналист', 'description': 'Создание новостного контента'},
        {'name': 'Фотограф', 'description': 'Фотосъемка'},
        {'name': 'Видеограф', 'description': 'Видеосъемка и монтаж'},
    ]

    for category_data in categories:
        category, created = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data['description']}
        )
        if created:
            print(f"✅ Создана категория: {category_data['name']}")
        else:
            print(f"ℹ️ Категория уже существует: {category_data['name']}")

    print(f"\n🎯 Всего категорий: {Category.objects.count()}")


if __name__ == '__main__':
    create_categories()