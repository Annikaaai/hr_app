import os
import django
import sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techno_work.settings')
django.setup()

from career_app.models import Category, Vacancy, Internship


def migrate_to_hierarchical_categories():
    """Мигрирует существующие данные к новой иерархической структуре категорий"""

    # Словарь для миграции старых категорий к новым подкатегориям
    migration_map = {
        'Программист': 'Программирование',
        'Веб-разработчик': 'Веб-разработка',
        'Мобильный разработчик': 'Мобильная разработка',
        'Data Scientist': 'Data Science',
        'DevOps': 'DevOps',
        'Тестировщик (QA)': 'Тестирование (QA)',
        'Системный администратор': 'DevOps',
        'Аналитик данных': 'Data Science',
        'Веб-дизайнер': 'Веб-дизайн',
        'Графический дизайнер': 'Графический дизайн',
        'UI/UX дизайнер': 'UI/UX дизайн',
        '3D-дизайнер': '3D-дизайн',
        'Маркетолог': 'Цифровой маркетинг',
        'SMM-специалист': 'SMM',
        'Копирайтер': 'Контент-маркетинг',
        'Продавец': 'Продажи',
        'Менеджер по продажам': 'Продажи',
        'Торговый представитель': 'Торговый персонал',
        'Проектный менеджер': 'Проектный менеджмент',
        'Продуктовый менеджер': 'Продуктовый менеджмент',
        'Офис-менеджер': 'Офис-менеджмент',
        'HR-менеджер': 'HR',
        'Бухгалтер': 'Бухгалтерия',
        'Финансовый аналитик': 'Финансовый анализ',
        'Экономист': 'Экономика',
        'Преподаватель': 'Преподавание',
        'Ученый': 'Научные исследования',
        'Лаборант': 'Научные исследования',
        'Врач': 'Медицина',
        'Медсестра/медбрат': 'Медицина',
        'Фармацевт': 'Фармацевтика',
        'Водитель': 'Водители',
        'Логист': 'Логистика',
        'Курьер': 'Курьерские услуги',
        'Инженер': 'Инженерия',
        'Техник': 'Инженерия',
        'Строитель': 'Строительство',
        'Архитектор': 'Архитектура',
        'Повар': 'Ресторанный бизнес',
        'Официант': 'Ресторанный бизнес',
        'Бариста': 'Ресторанный бизнес',
        'Администратор': 'Офис-менеджмент',
        'Юрист': 'Юриспруденция',
        'Переводчик': 'Переводы',
        'Журналист': 'Журналистика',
        'Фотограф': 'Фотография',
        'Видеограф': 'Видеопроизводство',
    }

    # Мигрируем вакансии
    vacancies_updated = 0
    for vacancy in Vacancy.objects.all():
        if vacancy.category and vacancy.category.name in migration_map:
            new_category_name = migration_map[vacancy.category.name]
            try:
                new_category = Category.objects.get(name=new_category_name)
                vacancy.category = new_category
                vacancy.save()
                vacancies_updated += 1
                print(f"✅ Вакансия '{vacancy.title}' мигрирована в категорию '{new_category_name}'")
            except Category.DoesNotExist:
                print(f"❌ Категория '{new_category_name}' не найдена")

    # Мигрируем стажировки
    internships_updated = 0
    for internship in Internship.objects.all():
        if internship.category and internship.category.name in migration_map:
            new_category_name = migration_map[internship.category.name]
            try:
                new_category = Category.objects.get(name=new_category_name)
                internship.category = new_category
                internship.save()
                internships_updated += 1
                print(f"✅ Стажировка '{internship.title}' мигрирована в категорию '{new_category_name}'")
            except Category.DoesNotExist:
                print(f"❌ Категория '{new_category_name}' не найдена")

    print(f"\n🎯 Миграция завершена!")
    print(f"📊 Обновлено вакансий: {vacancies_updated}")
    print(f"📊 Обновлено стажировок: {internships_updated}")


if __name__ == '__main__':
    migrate_to_hierarchical_categories()